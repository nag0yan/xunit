class TestResult():
  def __init__(self):
    self.runCount = 0
    self.failedCount = 0
    self.log = []
  def testStarted(self):
    self.runCount += 1
  def testPassed(self, name):
    self.log.append(f"{name}: passed")
  def testFailed(self, name):
    self.failedCount += 1
    self.log.append(f"{name}: failed")
  def setupFailed(self, name):
    self.failedCount += 1
    self.log.append(f"{name}: setup failed")
  def summary(self):
    return f"{self.runCount} run, {self.failedCount} failed"
  def details(self):
    return "\n".join(sorted(self.log))

class TestCase():
  def __init__(self, name):
    self.name = name
    self.log = ""
  def logging(self, process):
    self.log += f"{process} "
  def setup(self):
    pass
  def tearDown(self):
    pass
  def testMethod(self):
    pass
  def run(self, result):
    result.testStarted()
    try:
      self.logging("setup")
      self.setup()
      method = getattr(self, self.name)
      self.logging(self.name)
      method()
      result.testPassed(self.name)
    except SetupFailedException:
      result.setupFailed(self.name)
    except Exception:
      result.testFailed(self.name)
    self.logging("tearDown")
    self.tearDown()

class SetupFailedException(Exception):
  pass

class WasRun(TestCase):
  def setup(self):
    pass
  def testMethod(self):
    pass
  def testBrokenMethod(self):
    raise Exception
  def tearDown(self):
    pass

class SetupFailed(TestCase):
  def setup(self):
    raise SetupFailedException
  def testMethod(self):
    pass
  def tearDown(self):
    pass

class TestSuite():
  def __init__(self, testCaseClass = None):
    self.tests = []
    if testCaseClass is None:
      return
    for name in dir(testCaseClass):
      if name.startswith("test"):
        self.tests.append(testCaseClass(name))
  def add(self, test):
    self.tests.append(test)
  def run(self, result):
    for test in self.tests:
      test.run(result)
    return result
  pass

class TestCaseTest(TestCase):
  def setup(self):
    self.result = TestResult()
  def testTemplateMethod(self):
    test = WasRun("testMethod")
    test.run(self.result)
    assert test.log == "setup testMethod tearDown "
  def testResult(self):
    test = WasRun("testMethod")
    test.run(self.result)
    assert self.result.summary() == "1 run, 0 failed"
  def testFailedResult(self):
    test = WasRun("testBrokenMethod")
    test.run(self.result)
    assert self.result.summary() == "1 run, 1 failed"
  def testFailedResultFormating(self):
    self.result.testStarted()
    self.result.testFailed("testMethod")
    assert self.result.summary() == "1 run, 1 failed"
  def testSuite(self):
    suite = TestSuite()
    suite.add(WasRun("testMethod"))
    suite.add(WasRun("testBrokenMethod"))
    suite.run(self.result)
    assert self.result.summary() == "2 run, 1 failed"
  def testTearDownEvenFailed(self):
    test = WasRun("testBrokenMethod")
    test.run(self.result)
    assert test.log == "setup testBrokenMethod tearDown "
  def testSetupFailed(self):
    test = SetupFailed("testMethod")
    test.run(self.result)
    assert test.log == "setup tearDown "
    assert self.result.details() == "testMethod: setup failed"
  def testCaseToSuite(self):
    suite = TestSuite(WasRun)
    suite.run(self.result)
    assert self.result.summary() == "2 run, 1 failed"
  def testResultDetails(self):
    suite = TestSuite(WasRun)
    suite.run(self.result)
    assert self.result.details() == "testBrokenMethod: failed\ntestMethod: passed"
  
suite = TestSuite(TestCaseTest)
result = TestResult()
suite.run(result)
print(result.summary())
print()
print(result.details())