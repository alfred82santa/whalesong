import {
  ModelManager
} from './common.js';
import {
  command
} from '../manager.js';


export const STATE = {
  OPENING: "OPENING",
  PAIRING: "PAIRING",
  UNPAIRED: "UNPAIRED",
  UNPAIRED_IDLE: "UNPAIRED_IDLE",
  CONNECTED: "CONNECTED",
  TIMEOUT: "TIMEOUT",
  CONFLICT: "CONFLICT",
  UNLAUNCHED: "UNLAUNCHED",
  PROXYBLOCK: "PROXYBLOCK",
  TOS_BLOCK: "TOS_BLOCK",
  SMB_TOS_BLOCK: "SMB_TOS_BLOCK"
}

export const STREAM = {
  DISCONNECTED: "DISCONNECTED",
  SYNCING: "SYNCING",
  RESUMING: "RESUMING",
  CONNECTED: "CONNECTED"
}

export class StreamManager extends ModelManager {

  static mapModel(item) {
    return {
      backoffGeneration: item.backoffGeneration,
      canSend: item.canSend,
      hasSynced: item.hasSynced,
      isIncognito: item.isIncognito,
      lastPhoneMessage: item.lastPhoneMessage,
      launchGeneration: item.launchGeneration,
      launched: item.launched,
      pokeable: item.pokeable,
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