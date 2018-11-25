import {
  ModelManager
} from './common.js';
import {
  command
} from '../manager.js';

export class ConnManager extends ModelManager {
  @command
  async updatePushname({
    name
  }) {
    await this.model.updatePushname(name);
  }

  @command
  async canSetMyPushname() {
    await this.model.canSetMyPushname();
  }
}