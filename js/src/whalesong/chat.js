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

    this.addSubmanager('presence', manager.getSubmanager('presences').getSubmanager(this.model.id._serialized));
    this.addSubmanager('contact', manager.getSubmanager('contacts').getSubmanager(this.model.contact.id._serialized));
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

    if (!extraData['quotedMsg']) {
      if (linkDesc) {
        extraData['linkPreview'] = linkDesc;
      } else {
        extraData['linkPreview'] = await manager.getSubmanager('wap').queryLinkPreview({
          text
        });
      }
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
    let contact = new manager.getSubmanager('contacts').collection._model({
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
    let contact = manager.getSubmanager('contacts').collection.get(contactId);
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
  async setSubject({
    subject
  }) {
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

  @command
  async canSend() {
    return this.model.canSend();
  }

  @command
  async canArchive() {
    return this.model.canArchive();
  }

  @command
  async canPin() {
    return this.model.canPin();
  }

  @command
  async setArchive({
    archive
  }) {
    let result = await this.model.setArchive(archive);

    if (result.status === 200) {
      return true;
    }
    return false;
  }

  @command
  async setPin({
    pin
  }) {
    let result = await this.model.setPin(pin);

    if (result.status === 200) {
      return true;
    }
    return false;
  }

  @command
  async setGroupDesc({
    description
  }) {
    let result = await this.model.setGroupDesc(description);

    if (result.status === 200) {
      return true;
    }
    return false;
  }

  @command
  async sendStarMsgs({
    messageIds
  }) {
    let result = await this.model.sendStarMsgs(messageIds);

    if (result.status === 200) {
      return true;
    }
    return false;
  }

  @command
  async sendUnstarMsgs({
    messageIds
  }) {
    let result = await this.model.sendUnstarMsgs(messageIds);

    if (result.status === 200) {
      return true;
    }
    return false;
  }

  @command
  async sendNotSpam() {
    let result = await this.model.sendNotSpam();

    if (result.status === 200) {
      return true;
    }
    return false;
  }

  @command
  async sendSpamReport() {
    let result = await this.model.sendSpamReport();

    if (result.status === 200) {
      return true;
    }
    return false;
  }


}

export class ChatCollectionManager extends CollectionManager {

  static getModelManagerClass() {
    return ChatManager;
  }

  constructor(collection, mediaCollectionClass, createPeerForContact) {
    super(collection);

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
    picturePreview,
    picture
  }) {
    if (picturePreview) {
      picturePreview = 'data:image/jpeg;base64,' + picturePreview;
    }

    if (picture) {
      picture = 'data:image/jpeg;base64,' + picture;
    }
    return await this.collection.createGroup(
      name,
      picturePreview,
      picture,
      contactIds.map((item) => manager.getSubmanager('contacts').collection.get(item)).filter(Boolean));
  }

  @command
  async forwardMessagesToChats({
    messageIds,
    chatIds
  }) {
    let messages = messageIds.map((id) => manager.getSubmanager('messages').loadItem(id));
    let chats = chatIds.map((id) => this.loadItem(id));

    return await this.collection.forwardMessagesToChats(messages, chats);
  }
}