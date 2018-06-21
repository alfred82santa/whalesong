import {
  command
} from '../manager.js';
import {
  CollectionManager,
  ModelManager
} from './common.js';
import {
  MessageManager,
  MessageCollectionManager
} from './message.js';
import {
  ContactManager
} from './contact.js';
import {
  GroupMetadataManager
} from './groupMetadata.js';
import {
  SendMessageFail
} from './errors.js';
import b64toblob from 'b64-to-blob';


export class MsgLoadStateManager extends ModelManager {}

export class ChatManager extends ModelManager {

  static mapModel(item) {
    return Object.assign(ModelManager.mapModel(item), {
      kind: item.kind,
      isGroup: item.isGroup,
      contact: item.contact ? ContactManager.mapModel(item.contact) : null,
      groupMetadata: item.groupMetadata ? GroupMetadataManager.mapModel(item.groupMetadata) : null,
      lastReceivedKey: item.lastReceivedKey ? item.lastReceivedKey._serialized : null,
      msgs: null
    });
  }

  constructor(model) {
    super(model);
    this.addSubmanager('msgs', new MessageCollectionManager(model.msgs));
    this.addSubmanager('msgLoadState', new MsgLoadStateManager(model.msgs.msgLoadState));
  }

  @command
  async sendText({
    text,
    quotedMsgId,
    mentions,
    linkDesc
  }) {
    let msg = this.model.createMessageFromText(text)

    if (quotedMsgId) {
      let quotedMsg = this.model.msgs.get(quotedMsgId)
      if (quotedMsg) {
        msg.set(quotedMsg.contextInfo(this.model.id));
      }
    }

    if (mentions && mentions.length) {
      msg.mentionedJidList = mentions;
    }

    if (linkDesc) {
      msg.set(linkDesc);
    }

    let res = this.model.addAndSendMsg(msg);
    msg = await res[0];
    let r = await res[1];
    if (r === 'success') {
      return msg.id._serialized;
    }
    throw new SendMessageFail(
      `Send message ${msg.id._serialized} to chat ${this.model.id} fail`, {
        'msgId': msg.id._serialized,
        'chatId': this.model.id
      }
    );
  }

  @command
  async sendVCard({
    contactName,
    vcard,
    quotedMsgId
  }) {
    let msg = this.model.createMessageFromText('.')

    msg.body = vcard;
    msg.type = "vcard";
    msg.subtype = contactName;

    if (quotedMsgId) {
      let quotedMsg = this.model.msgs.get(quotedMsgId)
      if (quotedMsg) {
        msg.set(quotedMsg.contextInfo(this.model.id));
      }
    }

    let res = this.model.addAndSendMsg(msg);
    msg = await res[0];
    let r = await res[1];
    if (r === 'success') {
      return msg.id._serialized;
    }
    throw new SendMessageFail(
      `Send message ${msg.id._serialized} to chat ${this.model.id} fail`, {
        'msgId': msg.id._serialized,
        'chatId': this.model.id
      }
    );
  }

  @command
  async sendMedia({
    mediaData,
    contentType,
    filename,
    caption,
    quotedMsgId,
    mentions
  }) {
    let mediaBlob = b64toblob(mediaData, contentType);

    if (filename) {
      mediaBlob = new File([mediaBlob], filename, {
        'type': contentType
      });
    }

    let mc = this.buildMediaCollection();

    await mc.processFiles([mediaBlob], this.model, 1);
    let media = mc.models[0];

    let extraData = {};

    if (caption) {
      extraData.caption = caption
    }

    if (quotedMsgId) {
      extraData.quotedMsg = this.model.msgs.get(quotedMsgId)
    }

    if (mentions && mentions.length) {
      extraData.mentionedJidList = mentions;
    }

    await media.processPromise;

    let chat = this.model;

    let promise = new Promise(function(resolve) {
      function handler(item) {
        if (item.senderObj.isMe && item.isMedia && item.mediaData.filehash === media.mediaPrep._mediaData.filehash) {
          chat.msgs.off('add', handler);
          resolve(item);
        }
      }

      chat.msgs.on('add', handler);
      media.sendToChat(chat, extraData);
    });

    let msg = await promise;

    if (msg.promises.sendPromise) {
      try {
        await msg.promises.sendPromise;
      } catch (err) {
        throw new SendMessageFail(
          `Send message ${msg.id._serialized} to chat ${this.model.id} fail`, {
            'msgId': msg.id._serialized,
            'chatId': this.model.id
          }
        );
      }
    }

    return msg.id._serialized;
  }

  @command
  async sendSeen() {
    return await this.model.sendSeen();
  }

  @command
  async loadEarlierMessages() {
    return await this.model.loadEarlierMsgs();
  }

  @command
  async loadAllEarlierMessages() {
    while (!this.model.msgs.msgLoadState.noEarlierMsgs) {
      await this.model.loadEarlierMsgs();
    }
  }
}

export class ChatCollectionManager extends CollectionManager {

  static getModelManagerClass() {
    return ChatManager;
  }

  constructor(collection, mediaCollectionClass) {
    super(collection);
    ChatManager.prototype.buildMediaCollection = function() {
      return new mediaCollectionClass();
    }
  }


  @command
  async getActive() {
    return this.collection.active();
  }

  @command
  async resyncMessages() {
    return await this.collection.resyncMessages();
  }
}
