import {
  command
} from '../manager.js';
import {
  CollectionManager,
  ModelManager
} from './common.js';

export class StatusManager extends ModelManager {

  static mapModel(item) {
    return Object.assign(ModelManager.mapModel(item), {
      id: item.id._serialized
    });
  }
}

export class StatusCollectionManager extends CollectionManager {

  static getModelManagerClass() {
    return StatusManager;
  }

  @command
  async setMyStatus({
    status
  }) {
    let result = this.collection.setMyStatus(status);

    if (result.status === 200) {
      return true;
    }
    return false;
  }
}