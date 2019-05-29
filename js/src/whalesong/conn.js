import {
  ModelManager
} from './common.js';
import {
  command
} from '../manager.js';

export class ConnManager extends ModelManager {
  constructor(model, setPushname) {
    super(model);

    this._setPushname = setPushname;
  }

  @command
  async updatePushname({
    name
  }) {
    await this._setPushname(name);
  }

  @command
  async canSetMyPushname() {
    await this.model.canSetMyPushname();
  }
}