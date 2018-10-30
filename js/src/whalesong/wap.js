import {
  ModelManager
} from './common.js';

import {
  ChatManager
} from './chat.js';

import {
  command
} from '../manager.js';

export class WapManager extends ModelManager {

  @command
  async createGroup({
    name,
    contactIds
  }) {
    return ChatManager.mapModel(this.model.createGroup(name, contactIds));
  }
}