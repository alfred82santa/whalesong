import {
  ModelManager,
  CollectionManager
} from './common.js';
import {
  command
} from '../manager.js';
import {
  ValueError
} from '../errors.js';
import {
  ModelNotFound
} from './errors.js';


export class StickerManager extends ModelManager {

  static mapModel(item) {
    return Object.assign(ModelManager.mapModel(item), {
      _mediaObject: null
    });
  }


  @command
  async sendToChat({
    chatId,
    quotedMsgId
  }) {
    try {
      let chatManager = manager.getSubmanager('chats').getSubmanager(chatId);
    } catch (err) {
      throw new ModelNotFound(`Chat with ID "${id}" not found`);
    }

    if (quotedMsgId) {
      chatManager.model.composeQuotedMsg = this.model.msgs.get(quotedMsgId);
    }

    return await chatManager._sendMessage(
      () => this.model.sendToChat(chatManager.model),
      (item) => item.type === 'sticker' && item.filehash === this.model.filehash
    );
  }
}

export class StickerCollectionManager extends CollectionManager {

  static getModelManagerClass() {
    return StickerManager;
  }

  @command
  async fetch() {
    await this.collection.fetch();
  }
}

export class StickerPackManager extends ModelManager {

  getSubmanager(name) {
    try {
      return super.getSubmanager(name);
    } catch (err) {
      if (name === 'stickers') {
        return new StickerCollection(this.model.stickers);
      }
      throw err;
    }
  }
}

export class StickerPackCollectionManager extends CollectionManager {

  static getModelManagerClass() {
    return StickerPackManager;
  }

  @command
  async fetchPage({
    page
  }) {
    await this.collection.fetchAt(page);

    if (!this.collection.pageFetchStates[page]) {
      throw ValueError(`Page ${page} does not exist`);
    }
  }

  @command
  async fetchAllPages() {
    try {
      let page = 0;
      while (true) {
        await this.fetchPage({
          page: page
        });
      }
    } catch (err) {};
  }

  @command
  async reset() {
    this.collection.reset();
  }
}