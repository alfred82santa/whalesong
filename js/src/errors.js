export class BaseError {
  constructor(message) {
    this.message = message;
    this.name = this.constructor.name;
    this.params = arguments[1] || {};
  }
}


export class ManagerNotFound extends BaseError {
  constructor(manager = '#unknown#') {
    super(`Manager ${manager} not found`);
  }
}

export class CommandNotFound extends BaseError {
  constructor(command = '#unknown#') {
    super(`Command ${command} not found`);
  }
}

export class ValueError extends BaseError {}

export class StopIterator extends BaseError {};

export class StopMonitor extends BaseError {};