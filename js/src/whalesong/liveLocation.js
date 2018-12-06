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
  command
} from '../manager.js';


export class ParticipantManager extends ModelManager {

  static mapModel(item) {
    return Object.assign(ModelManager.mapModel(item), {
      id: item.id._serialized,
      msg: MessageManager.mapModel(item.msg),
      contact: ContactManager.mapModel(item.contact),
      isMe: item.isMe,
      isState: item.isState,
      valid: item.valid,
      disabled: item.disabled
    });
  }
}

export class ParticipantCollectionManager extends CollectionManager {

  static getModelManagerClass() {
    return ParticipantManager;
  }
}


export class LiveLocationManager extends ModelManager {

  static mapModel(item) {
    return Object.assign(ModelManager.mapModel(item), {
      id: item.id._serialized,
      participants: item.participants.map((p) => ParticipantManager.mapModel(p))
    });
  }

  constructor(model) {
    super(model);
    this.addSubmanager('participants', new ParticipantCollectionManager(model.participants));
  }

  @command
  async subscribe() {
    return await this.model.startViewingMap();
  }

  @command
  async unsubscribe() {
    return await this.model.stopViewingMap();
  }

  @command
  async stopMyLiveLocation() {
    return await this.model.stopMyLiveLocation();
  }

}

export class LiveLocationCollectionManager extends CollectionManager {

  static getModelManagerClass() {
    return LiveLocationManager;
  }
}