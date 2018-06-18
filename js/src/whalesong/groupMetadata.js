import {
  CollectionManager,
  ModelManager
} from './common.js';

export class GroupMetadataManager extends ModelManager {}

export class GroupMetadataCollectionManager extends CollectionManager {

  static getModelManagerClass() {
    return GroupMetadataManager;
  }
}