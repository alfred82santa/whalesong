import {
  command,
  Iterator
} from "../manager";
import {
  CollectionManager,
  ModelManager
} from "./common";
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
    messageId,
  }) {
    return await this.model.sendReadStatus(
      this.getSubmanager('msgs').loadItem(messageId).id,
      this.model.id
    );
  }

}

export class StatusV3CollectionManager extends CollectionManager {
  static getModelManagerClass() {
    return StatusV3Manager;
  }

  @command
  async getUnexpired({
    unread
  }) {
    const statuses = await this.collection.getUnexpired(unread);
    return Iterator.fromArray(statuses, StatusV3Manager.mapModel);
  }

  @command
  async sync() {
    await this.collection.sync();
  }

  @command
  async getMyStatus() {
    return await this.collection.getMyStatus();
  }
}