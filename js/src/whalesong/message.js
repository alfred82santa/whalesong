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

  getSubmanager(name) {
    try {
      return super.getSubmanager(name);
    } catch (err) {
      if (name === 'msgInfo') {
        try {
          return manager.getSubmanager('messageInfos').getSubmanager(this.model.id._serialized);
        } catch (err2) {}
      }

      throw err;
    }
  }

  @command
  async fetchInfo() {
    return await manager.getSubmanager('messageInfos').fetchByMessage(this.model);
  }
}

export class MessageCollectionManager extends CollectionManager {

  static getModelManagerClass() {
    return MessageManager;
  }

  constructor(collection) {
    super();
    this.collection = collection;
  }

  @monitor
  async monitorNew() {
    return new CollectionItemMonitor(
      this.collection,
      'add', (item) => item.isNewMsg && !item.isSentByMeFromWeb ? this.mapItem(item) : null
    );
  }
}