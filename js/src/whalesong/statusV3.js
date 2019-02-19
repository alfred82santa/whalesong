import { command, Iterator } from "../manager";
import { CollectionManager, ModelManager } from "./common";
import {
  MessageCollectionManager
} from "./message";
import {
  ContactManager
} from './contact.js';

export class StatusV3Manager extends ModelManager {
  static mapModel(item) {
    return Object.assign(ModelManager.mapModel(item), {
      id: item.id._serialized,
      contact: item.contact ? ContactManager.mapModel(item.contact) : null,
      msgs: null,
      expireTs: item.expireTs,
      hasUnread: item.hasUnread,
      lastReceivedKey: item.lastReceivedKey ? item.lastReceivedKey._serialized : null,
      totalCount: item.totalCount,
      unreadCount: item.unreadCount,
      readKeys: item.readKeys
    });
  }

  constructor(model) {
    super(model);

    this.addSubmanager('msgs', new MessageCollectionManager(model.msgs));
    this.addSubmanager('contact', new ContactManager(this.model.contact));
  }

  @command
  async sendReadStatus({
    readMessage,
    fromUser,
  }) {
    return await this.model.sendReadStatus(readMessage, fromUser);
  }

  @command
  async loadMore() {
    return this.model.loadMore();
  }
}

export class StatusV3CollectionManager extends CollectionManager {
  static getModelManagerClass() {
    return StatusV3Manager;
  }

  transformToIterator(items, mapFn) {
    return new Iterator(
      (partialResult) => items.forEach(
        item => partialResult(
          mapFn(item)
        )
      )
    );
  }

  @command
  async getStatus({
    unread
  }) {
    const statuses = await this.collection.getUnexpired(unread);
    return this.transformToIterator(statuses, StatusV3Manager.mapModel);
  }

  @command
  async sync() {
    return await this.collection.sync();
  }

  @command
  async getMyStatus() {
    return await this.collection.getMyStatus();
  }
}