import {
  command
} from '../manager.js';
import {
  CollectionManager,
  ModelManager
} from './common.js';
import {
  MessageManager
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

  @command
  async getMessages() {
    return new Iterator(
      (partialResult) => this.model.msgs.forEach(
        (item) => partialResult(
          MessageManager.mapItem(item)
        )
      )
    );
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

  @command
  async getChatMessages({
    id
  }) {
    let chat = this.loadItem(id);

    let chatManager = new ChatManager(chat);
    return await chatManager.getMessages();
  }

  @command
  async sendTextToChat({
    id,
    text,
    quotedMsgId,
    mentions,
    linkDesc
  }) {
    let chat = this.loadItem(id);

    let chatManager = new ChatManager(chat);
    return await chatManager.sendText({
      text: text,
      quotedMsgId: quotedMsgId,
      mentions: mentions,
      linkDesc: linkDesc
    });
  }

  @command
  async sendVCardToChat({
    id,
    contactName,
    vcard,
    quotedMsgId
  }) {
    let chat = this.loadItem(id);

    let chatManager = new ChatManager(chat);
    return await chatManager.sendVCard({
      contactName: contactName,
      vcard: vcard,
      quotedMsgId: quotedMsgId
    });
  }

  @command
  async sendMediaToChat({
    id,
    mediaData,
    contentType,
    filename,
    caption,
    quotedMsgId,
    mentions
  }) {
    let chat = this.loadItem(id);

    let chatManager = new ChatManager(chat);
    return await chatManager.sendMedia({
      mediaData: mediaData,
      contentType: contentType,
      filename: filename,
      caption: caption,
      quotedMsgId: quotedMsgId,
      mentions: mentions
    });
  }

  @command
  async sendSeenToChat({
    id
  }) {
    let chat = this.loadItem(id);

    let chatManager = new ChatManager(chat);
    return await chatManager.sendSeen();
  }
}