import {
  CollectionManager,
  ModelManager
} from './common.js';
import {
  command
} from '../manager.js';


export class MessageAckManager extends ModelManager {

  static mapModel(item) {
    return Object.assign(ModelManager.mapModel(item), {
      id: item.id._serialized
    });
  }
}

export class MessageAckCollectionManager extends CollectionManager {

  static getModelManagerClass() {
    return MessageAckManager;
  }
}


export class MessageInfoManager extends ModelManager {

  static mapModel(item) {
    return Object.assign(ModelManager.mapModel(item), {
      id: item.id._serialized,
      delivery: item.delivery.map((item) => MessageAckManager.mapModel(item)),
      played: item.delivery.map((item) => MessageAckManager.mapModel(item)),
      read: item.delivery.map((item) => MessageAckManager.mapModel(item))
    });
  }

  getSubmanager(name) {
    try {
      return super.getSubmanager(name);
    } catch (err) {
      switch (name) {
        case 'read':
        case 'delivery':
        case 'played':
          return new MessageAckCollectionManager(this.model[name]);
        default:
          throw err;
      }
    }
  }
}

export class MessageInfoCollectionManager extends CollectionManager {

  static getModelManagerClass() {
    return MessageInfoManager;
  }

  @command
  async fetch({
    message_id
  }) {
    let msg = await manager.getSubmanager('messages').loadItem(message_id);

    return await this.fetchByMessage(msg.id);
  }

  async fetchByMessage(msg) {
    return MessageInfoManager.mapModel(await this.collection.find(msg.id));
  }
}