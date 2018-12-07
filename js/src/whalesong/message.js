import {
  CollectionManager,
  ModelManager,
  CollectionItemMonitor
} from './common.js';
import {
  monitor,
  command
} from '../manager.js';
import {
  ContactManager
} from './contact.js';
import {
  ChatManager
} from './chat.js';


export class MessageManager extends ModelManager {

  static mapModel(item) {
    return Object.assign(ModelManager.mapModel(item), {
      id: item.id._serialized,
      senderObj: item.senderObj ? ContactManager.mapModel(item.senderObj) : null,
      chat: item.chat ? ChatManager.mapModel(item.chat) : null,

      isGroupMsg: item.isGroupMsg,
      isLink: item.isLink,
      isMMS: item.isMMS,
      isMedia: item.isMedia,
      isNotification: item.isNotification,
      isPSA: item.isPSA,
      hasPromises: item.promises.length ? true : false,

      streamingSidecar: null
    });
  }

  @command
  async fetchInfo() {
    let result = await manager.getSubmanager('messageInfos').fetchByMessage(this.model);
    this.addSubmanager('msgInfo', manager.getSubmanager('messageInfos').getSubmanager(this.model.id._serialized));
    return result;
  }

  @command
  async canStar() {
    return this.model.canStar();
  }

  @command
  async star() {
    return await manager.getSubmanager('chats')
      .getSubmanager(this.model.chat.id)
      .sendStarMsgs({
        'messageIds': [this.model.id]
      });
  }

  @command
  async unstar() {
    return await manager.getSubmanager('chats')
      .getSubmanager(this.model.chat.id)
      .sendUnstarMsgs({
        'messageIds': [this.model.id]
      });
  }

  @command
  async canRevoke() {
    return this.model.canRevoke();
  }

  @command
  async revoke({
    clearMedia
  }) {
    return await this.model.sendRevoke(clearMedia);
  }
}

export class MessageCollectionManager extends CollectionManager {

  static getModelManagerClass() {
    return MessageManager;
  }

  @monitor
  async monitorNew() {
    return new CollectionItemMonitor(
      this.collection,
      'add', (item) => item.isNewMsg && !item.isSentByMeFromWeb ? this.mapItem(item) : null
    );
  }
}