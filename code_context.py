import inspect, time, datetime, os

def info(inspect_stack=None):
  if inspect_stack:
    callerframerecord = inspect_stack[0]    # 0 represents this line, 1 represents line at caller
  else:
    callerframerecord = inspect.stack()[0]    # 0 represents this line, 1 represents line at caller
  frame = callerframerecord[0]
  info = inspect.getframeinfo(frame)
  return str(info.filename) + ' - ' + str(info.function) + ' - ' + str(info.lineno)

def time_check(inspect_stack=None):
  print('⏰ TIME CHECK: ' + info(inspect_stack) + ': ' + str(datetime.datetime.now()))
  # print('⏰ TIME CHECK: ' + str(datetime.datetime.now()))
  if 'LAST_TIME_CHECK' in os.environ:
    print('⏳ DURATION: ' + str(time.time() - float(os.environ['LAST_TIME_CHECK'])))
  os.environ['LAST_TIME_CHECK'] = str(time.time())
