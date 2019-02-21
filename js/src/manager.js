import {
  BaseError,
  ManagerNotFound,
  CommandNotFound,
  StopMonitor,
  StopIterator
} from './errors.js';

export const ResultTypes = {
  ERROR: 'ERROR',
  FINAL: 'FINAL',
  PARTIAL: 'PARTIAL'
}

export const COMMAND_SEPARATOR = '|';

export class ResultManager {

  constructor() {
    this._results = [];
  }

  setResult(exId, type, params) {
    let data = {
      'exId': exId,
      'type': type,
      'params': params || {}
    }

    if (window.whalesongPushResult !== undefined) {
      window.whalesongPushResult(data);
    } else {
      this._results.push(data);
    }
  }

  setFinalResult(exId, params) {
    this.setResult(exId, ResultTypes.FINAL, params);
  }

  setPartialResult(exId, params) {
    this.setResult(exId, ResultTypes.PARTIAL, params);
  }

  setErrorResult(exId, params) {
    this.setResult(exId, ResultTypes.ERROR, params);
  }

  getResults() {
    let results = this._results;
    this._results = [];
    return results;
  }
}

export class Monitor {
  constructor(obj, evt, mapFn) {
    this.obj = obj;
    this.evt = evt;
    this.mapFn = mapFn;
    this.promise = new Promise(resolve => this._resolveFunc = resolve);
  }

  mapEventResult(...args) {
    if (this.mapFn) {
      return this.mapFn(...args);
    }
    return {
      'args': args
    };
  }

  handler(partialResult, ...args) {
    let result = this.mapEventResult(...args);

    if (result) {
      partialResult(result);
    }
  }

  initMonitor(partialResult) {}
  finishMonitor(partialResult) {}

  _addHandler(handler) {
    this.obj.on(this.evt, handler, this);
  }

  _removeHandler(handler) {
    this.obj.off(this.evt, handler, this);
  }

  async monitor(partialResult) {
    let handler = this.handler.bind(this, partialResult);
    this.initMonitor(partialResult);
    this._addHandler(handler);
    await this.promise;
    this._removeHandler(handler);
    this.finishMonitor(partialResult);
    throw new StopMonitor();
  }

  stopMonitor() {
    this._resolveFunc();
  }
}


export class MonitorManager {
  constructor() {
    this.monitors = {};
  }

  addMonitor(exId, monitor) {
    this.monitors[exId] = monitor;
  }

  removeMonitor(exId) {
    if (!(exId in this.monitors)) {
      return false;
    }

    this.monitors[exId].stopMonitor();
    delete this.monitors[exId];
    return true;
  }
}


export class Iterator {

  constructor(fn) {
    this.fn = fn;
  }

  static fromArray(arr, mapFn) {
    return new Iterator(
      partialResult => arr.forEach(
        item => partialResult(
          mapFn(item)
        )
      )
    );
  }

  async iter(partialResult) {
    await Promise.resolve(this.fn((item) => partialResult({
      'item': item
    })));
    throw new StopIterator();
  }
}


export function command(target, name, descriptor) {
  target.commands = Object.assign({}, target.commands || {});
  target.commands[name] = {
    'type': 'command'
  };
  return descriptor;
}

export function monitor(target, name, descriptor) {
  target.commands = Object.assign({}, target.commands || {});
  target.commands[name] = {
    'type': 'monitor'
  };
  return descriptor;
}


export class CommandManager {

  constructor() {
    this.commands = this.commands || {};
    this.submanagers = {};
  }

  addSubmanager(name, manager) {
    this.submanagers[name] = manager;
  }

  getSubmanager(name) {
    let manager = this.submanagers[name];
    if (!manager) {
      throw new ManagerNotFound(name);
    }
    return manager;
  }

  @command
  async getSubmanagers() {
    let submanagers = {};

    for (let sm in this.submanagers) {
      submanagers[sm] = {
        'class': this.submanagers[sm].constructor.name
      }
    }

    return submanagers;
  }

  @command
  async removeSubmanager(name) {
    delete this.submanagers[name]
  }

  async executeCommand(command, params) {

    if (command.indexOf(COMMAND_SEPARATOR) >= 0) {
      let deco = command.split(COMMAND_SEPARATOR);
      let manager = deco.shift(),
        cmd = deco.join(COMMAND_SEPARATOR);

      manager = this.getSubmanager(manager);

      return await manager.executeCommand(cmd, params);
    }

    if (!(command in this.commands)) {
      throw new CommandNotFound(command);
    }

    return await this[command](params);
  }

  @command
  async getCommands() {
    let commands = Object.assign({}, this.commands);

    for (let sm in this.submanagers) {
      let subcommands = await this.submanagers[sm].getCommands();
      for (let cm in subcommands) {
        commands[sm + COMMAND_SEPARATOR + cm] = subcommands[cm];
      }
    }

    return commands;
  }
}

export default class MainManager extends CommandManager {

  constructor() {
    super();
    this.resultManager = new ResultManager();
    this.monitorManager = new MonitorManager(this.resultManager);
  }

  poll(newExecutions) {
    let errors = [];
    if (newExecutions) {
      for (let idx in newExecutions) {
        let executionsObj = newExecutions[idx];

        if (!executionsObj['exId']) {
          errors.push({
            'name': 'RequiredExecutionId',
            'message': 'Execuction ID is required',
            'executionsObj': executionsObj
          });

          continue;
        }

        if (!executionsObj['command']) {
          errors.push({
            'name': 'RequiredCommandName',
            'message': 'Command name is required',
            'executionsObj': executionsObj
          });
          continue;
        }
        try {
          this.executeCommand(executionsObj['exId'], executionsObj['command'], executionsObj['params'] || {});
        } catch (err) {
          console.error(err, executionsObj);
          throw err;
        }
      }
    }

    return {
      'results': this.resultManager.getResults(),
      'errors': errors
    }
  }

  async executeCommand(exId, command, params) {
    try {
      console.log(exId, command, params);
      let result = await super.executeCommand(
        command,
        params
      );
      if (result instanceof Monitor) {
        this.monitorManager.addMonitor(exId, result);
        await result.monitor(
          (partial) => this.resultManager.setPartialResult(exId, partial)
        );
      } else if (result instanceof Iterator) {
        await result.iter(
          (partial) => this.resultManager.setPartialResult(exId, partial)
        );
      }
      console.log(exId, command, result)
      this.resultManager.setFinalResult(exId, result);
    } catch (err) {
      console.error(err, command, params);
      if ((err instanceof Error) || (err instanceof BaseError)) {
        this.resultManager.setErrorResult(exId, {
          'name': err.displayName || err.name,
          'message': err.message,
          'params': err.params || {}
        });
      } else {
        this.resultManager.setErrorResult(exId, {
          'err': err
        });
      }
    }
  }

  @command
  async stopMonitor({
    monitorId
  }) {
    return this.monitorManager.removeMonitor(monitorId);
  }

  @command
  async ping() {
    return 'pong';
  }
}