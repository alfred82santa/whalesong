import {
  ModelManager
} from './common.js';
import {
  command
} from '../manager.js';


export class DisplayInfoManager extends ModelManager {

  static mapModel(item) {
    return {
      available: item.available,
      clientExpired: item.clientExpired,
      couldForce: item.couldForce,
      displayInfo: item.displayInfo,
      hardExpired: item.hardExpired,
      info: item.info,
      isState: item.isState,
      obscurity: item.obscurity,
      phoneAuthed: item.phoneAuthed,
      resumeCount: item.resumeCount,
      uiActive: item.uiActive,
      mode: item.mode
    };
  }

  @command
  async markAvailable() {
    this.model.markAvailable();
  }

  @command
  async markUnavailable() {
    this.model.markUnavailable();
  }

  @command
  async unobscure() {
    this.model.unobscure();
  }
}