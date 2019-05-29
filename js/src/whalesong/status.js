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

  constructor(model, setMyStatus) {
    super(model);

    this._setMyStatus = setMyStatus;
  }

  @command
  async setMyStatus({
    status
  }) {
    let result = this._setMyStatus(status);

    if (result.status === 200) {
      return true;
    }
    return false;
  }
}