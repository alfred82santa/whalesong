import {
  CollectionManager,
  ModelManager
} from './common.js';
import {
  command
} from '../manager.js';
import {
  OperationNotAllowed
} from '../errors.js';


export class MuteManager extends ModelManager {

  static mapModel(item) {
    return Object.assign(ModelManager.mapModel(item), {
      id: item.id._serialized ? item.id._serialized : item.id,
      isMuted: item.isMuted,
      isState: item.isState
    });
  }

  @command
  async mute({
    expiration
  }) {
    if (this.model.id === 'global_mute') {
      throw OperationNotAllowed('Global mute can not be managed from Mute manager, use Mute collection.')
    }
    return await this.model.mute(expiration, true);
  }

  @command
  async canMute({
    expiration
  }) {
    return this.model.canMute();
  }

  @command
  async unmute({
    expiration
  }) {
    if (this.model.id === 'global_mute') {
      throw OperationNotAllowed('Global mute can not be managed from Mute manager, use Mute collection.')
    }
    return await this.model.unmute(true);
  }

}

export class MuteCollectionManager extends CollectionManager {

  static getModelManagerClass() {
    return GroupMetadataManager;
  }

  @command
  async getGlobalNotifications() {
    return this.collection.getGlobalNotifications();
  }

  @command
  async setGlobalNotifications({
    state
  }) {
    return this.collection.setGlobalNotifications(state);
  }

  @command
  async getGlobalPreviews() {
    return this.collection.getGlobalPreviews();
  }

  @command
  async setGlobalPreviews({
    state
  }) {
    return this.collection.setGlobalPreviews(state);
  }

  @command
  async getGlobalSounds() {
    return this.collection.getGlobalSounds();
  }

  @command
  async setGlobalSounds({
    state
  }) {
    return this.collection.setGlobalSounds(state);
  }

}