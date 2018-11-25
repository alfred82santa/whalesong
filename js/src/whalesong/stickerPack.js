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
      await this.model.downloadMedia();

      let chatManager = manager.getSubmanager('chats').getSubmanager(chatId);
    } catch (err) {
      throw new ModelNotFound(`Chat with ID "${chatId}" not found`);
    }

    if (quotedMsgId) {
      chatManager.model.composeQuotedMsg = chatManager.model.msgs.get(quotedMsgId);
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

  constructor(model) {
    super(model);

    this.addSubmanager('stickers', new StickerCollectionManager(this.model.stickers));
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

    let prIdx = this.collection.pageWithIndex(page);

    if (prIdx < page) {
      throw new ValueError(`Page ${page} does not exist`);
    }

    if (this.collection.pageFetchStates[prIdx] === 'SUCCESS') {
      return;
    }

    await this.collection.fetchAt(page);

    await this.collection._pageFetchPromises[prIdx];

    if (!this.collection.pageFetchStates[prIdx]) {
      throw new ValueError(`Page ${page} does not exist`);
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
        page++;
      }
    } catch (err) {};
  }

  @command
  async reset() {
    return this.collection.reset();
  }

  @command
  async getItemByName({
    name
  }) {
    let l = this.collection.where({
      name: name
    });

    if (l.length === 0) {
      throw new ModelNotFound(`Sticker pack with name "${name}" not found`);
    }

    return this.mapItem(l[0]);
  }
}