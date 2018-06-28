import {
  CollectionManager,
  ModelManager,
  CollectionItemMonitor
} from './common.js';
import {
  monitor
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

      streamingSidecar: null
    });
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
      'add',
      (item) => item.isNewMsg && !item.isSentByMeFromWeb? this.mapItem(item) : null
    );
  }
}
