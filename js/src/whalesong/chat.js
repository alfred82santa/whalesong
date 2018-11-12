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
  SendMessageFail,
  ModelNotFound
} from './errors.js';
import b64toblob from 'b64-to-blob';


export class MsgLoadStateManager extends ModelManager {}

export class ChatManager extends ModelManager {

  static mapModel(item) {
    return Object.assign(ModelManager.mapModel(item), {
      id: item.id._serialized,
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
    try {
      this.addSubmanager('metadata', new GroupMetadataManager(this.model.groupMetadata));
    } catch (err) {}
  }

  async _sendMessage(send_fn, check_fn) {
    let chat = this.model;

    let promise = new Promise(function(resolve) {
      function handler(item) {
        try {
          if (item.isNewMsg && item.isSentByMeFromWeb && check_fn(item)) {
            chat.msgs.off('add', handler);
            resolve(item);
          }
        } catch (err) {
          console.error(err);
        }
      }
      chat.msgs.on('add', handler);
      send_fn()
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
  async sendText({
    text,
    quotedMsgId,
    mentions,
    linkDesc
  }) {
    let extraData = {};
    if (quotedMsgId) {
      let quotedMsg = this.model.msgs.get(quotedMsgId)
      if (quotedMsg) {
        extraData['quotedMsg'] = quotedMsg;
      }
    }

    if (mentions && mentions.length) {
      extraData['mentionedJidList'] = mentions;
    }

    if (linkDesc) {
      extraData['linkPreview'] = linkDesc;
    }

    let chat = this.model;

    return await this._sendMessage(
      () => this.model.sendMessage(text, extraData),
      (item) => item.body === text && item.type === 'chat'
    );
  }

  async _sendContact(contact, quotedMsgId) {
    let quotedMsg;
    if (quotedMsgId) {
      quotedMsg = this.model.msgs.get(quotedMsgId);
    }

    return await this._sendMessage(
      () => this.model.sendContact(contact, quotedMsg),
      (item) => item.subtype && item.type === 'vcard'
    );
  }

  @command
  async sendContactPhone({
    contactName,
    phoneNumber,
    quotedMsgId
  }) {
    let contact = new this.contacts._model({
      id: phoneNumber + '@c.us',
      name: contactName
    });

    return await this._sendContact(contact, quotedMsgId);
  }

  @command
  async sendContact({
    contactId,
    quotedMsgId
  }) {
    let contact = this.contacts.get(contactId);
    if (!contact) {
      throw ModelNotFound(`Contact with ID "${contactId}" not found`);
    }

    return await this._sendContact(contact, quotedMsgId);
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

    return await this._sendMessage(
      () => media.sendToChat(this.model, extraData),
      (item) => (item.isMedia || item.isDoc) && item.mediaData.filehash === media.mediaPrep._mediaData.filehash
    );
  }

  @command
  async leaveGroup() {
    return await this.model.sendExit();
  }

  @command
  async deleteChat() {
    return await this.model.sendDelete();
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

  @command
  async setSubject({subject}) {
    await this.model.setSubject(subject);
  }

  @command
  async markComposing() {
    this.model.markComposing();
  }

  @command
  async markRecording() {
    this.model.markRecording();
  }

  @command
  async markPaused() {
    this.model.markPaused();
  }
}

export class ChatCollectionManager extends CollectionManager {

  static getModelManagerClass() {
    return ChatManager;
  }

  constructor(collection, contactCollection, mediaCollectionClass, createPeerForContact) {
    super(collection);

    ChatManager.prototype.contacts = contactCollection;

    ChatManager.prototype.buildMediaCollection = function() {
      return new mediaCollectionClass();
    }

    this.createPeerForContact = function(contactId) {
      return new createPeerForContact(contactId);
    }
  }


  @command
  async getActive() {
    return this.collection.active();
  }

  @command
  async ensureChatWithContact({
    contactId
  }) {
    let result = this.collection.get(contactId);
    if (!result) {
      result = await this.collection.find(this.createPeerForContact(contactId));
    }
    return this.constructor.getModelManagerClass().mapModel(result);
  }

  @command
  async resyncMessages() {
    return await this.collection.resyncMessages();
  }

  @command
  async createGroup({
    name,
    contactIds,
    picture
  }) {
    if (picture) {
      picture = 'data:image/jpeg;base64,' + picture;
    }
    return await this.collection.createGroup(
      name,
      picture,
      picture,
      contactIds.map((item) => this.contacts.get(item)).filter(Boolean));
  }
}
