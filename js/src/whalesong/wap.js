import {
  ModelManager
} from './common.js';

import {
  command
} from '../manager.js';

export class WapManager extends ModelManager {

  @command
  async queryExist({
    contactId
  }) {
    let result = await this.model.queryExist(contactId);
    if (result.status === 200) {
      return true;
    }
    return false;
  }

  @command
  async queryLinkPreview({
    text
  }) {
    let result = await this.model.queryLinkPreview(text);

    if (result.status && result.status !== 200) {
      return;
    }

    return result;
  }
}