import {
  ModelManager
} from './common.js';
import {
  command
} from '../manager.js';


export class StreamManager extends ModelManager {

  static mapModel(item) {
    return {
      backoffGeneration: item.backoffGeneration,
      canSend: item.canSend,
      hasSynced: item.hasSynced,
      isIncognito: item.isIncognito,
      //      lastPhoneMessage: item.lastPhoneMessage,
      launchGeneration: item.launchGeneration,
      launched: item.launched,
      retryTimestamp: item.retryTimestamp,
      state: item.state,
      stream: item.stream,
      syncTag: item.syncTag
    };
  }

  @command
  async poke() {
    this.model.poke();
  }

  @command
  async takeover() {
    this.model.takeover();
  }
}