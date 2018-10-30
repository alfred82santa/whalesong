import {
  CollectionManager,
  ModelManager
} from './common.js';
import {
  command
} from '../manager.js';

export class ParticipantManager extends ModelManager {

  static mapModel(item) {
    return Object.assign(ModelManager.mapModel(item), {
      id: item.id._serialized
    });
  }
}

export class ParticipantCollectionManager extends CollectionManager {

  static getModelManagerClass() {
    return ParticipantManager;
  }

  _getParticipants(contactIds) {
    return contactIds.map((contactId) => this.collection.get(contactId)).filter(Boolean);
  }

  _getContacts(contactIds) {
    return contactIds.map((contactId) => manager.getSubmanager('contacts').collection.get(contactId)).filter(Boolean);
  }

  @command
  async addParticipants({
    contactIds
  }) {
    let contacts = this._getContacts(contactIds);
    return await this.collection.addParticipants(contacts)
  }

  @command
  async canAdd({
    contactId
  }) {
    let contact = manager.getSubmanager('contacts').collection.get(contactId);
    if (!contact) {
      return false;
    }
    return this.collection.canAdd(contacts)
  }

  @command
  async removeParticipants({
    contactIds
  }) {
    let participants = this._getParticipants(contactIds);
    return await this.collection.removeParticipants(participants)
  }

  @command
  async canRemove({
    contactId
  }) {
    let participant = this.collection.get(contactId);
    if (!participant) {
      return false;
    }
    return this.collection.canRemove(participant)
  }

  @command
  async promoteParticipants({
    contactIds
  }) {
    let participants = this._getParticipants(contactIds);
    return await this.collection.promoteParticipants(participants)
  }

  @command
  async canPromote({
    contactId
  }) {
    let participant = this.collection.get(contactId);
    if (!participant) {
      return false;
    }
    return this.collection.canPromote(participant)
  }

  @command
  async demoteParticipants({
    contactIds
  }) {
    let participants = this._getParticipants(contactIds);
    return await this.collection.demoteParticipants(participants)
  }

  @command
  async canDemote({
    contactId
  }) {
    let participant = this.collection.get(contactId);
    if (!participant) {
      return false;
    }
    return this.collection.canDemote(participant)
  }
}


export class GroupMetadataManager extends ModelManager {

  static mapModel(item) {
    return Object.assign(ModelManager.mapModel(item), {
      groupInviteLink: item.groupInviteLink,
      inviteCode: item.inviteCode
    });
  }

  constructor(model) {
    super(model);
    this.addSubmanager('participants', new ParticipantCollectionManager(model.participants));
  }

  @command
  async groupInviteCode() {
    return await this.model.groupInviteCode();
  }

  @command
  async revokeGroupInvite() {
    return await this.model.revokeGroupInvite();
  }

}

export class GroupMetadataCollectionManager extends CollectionManager {

  static getModelManagerClass() {
    return GroupMetadataManager;
  }
}