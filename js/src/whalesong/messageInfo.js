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

  constructor(model) {
    super(model);

    this.addSubmanager('read', new MessageAckCollectionManager(this.model.read));
    this.addSubmanager('delivery', new MessageAckCollectionManager(this.model.delivery));
    this.addSubmanager('played', new MessageAckCollectionManager(this.model.played));
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