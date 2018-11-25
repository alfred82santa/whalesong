import {
  command
} from '../manager.js';
import {
  CollectionManager,
  ModelManager
} from './common.js';


export class ChatStateManager extends ModelManager {

  static mapModel(item) {
    return Object.assign(ModelManager.mapModel(item), {
      id: item.id._serialized ? item.id._serialized : item.id,
    });
  }

  @command
  async subscribe() {
    return this.mapModel(await this.model.subscribe());
  }
}

export class ChatStateCollectionManager extends CollectionManager {
  static getModelManagerClass() {
    return ChatStateManager;
  }
}

export class PresenceManager extends ModelManager {

  static mapModel(item) {
    return Object.assign(ModelManager.mapModel(item), {
      id: item.id._serialized,
      chatActive: item.chatActive,
      forceDisplay: false,
      hasData: false,
      isOnline: false,
      isSubscribed: false,
      chatstate: item.isUser ? ChatStateManager.mapModel(item.chatstate) : null,
      chatstates: item.isGroup ? item.chatstates.map((state) => ChatStateManager.mapModel(state)) : null
    });
  }

  constructor(model) {
    super(model);

    this.addSubmanager('chatStates', new ChatStateCollectionManager(this.model.chatstates));
    this.addSubmanager('chatState', new ChatStateManager(this.model.chatstate));
  }

  @command
  async update() {
    return this.constructor.mapModel(await this.model.update());
  }
}

export class PresenceCollectionManager extends CollectionManager {
  static getModelManagerClass() {
    return PresenceManager;
  }
}