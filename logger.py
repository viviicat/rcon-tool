import SourceLib.SourceLog

class ParserLogger(SourceLib.SourceLog.SourceLogParser):
  def parse(self, line):
    SourceLib.SourceLog.SourceLogParser.parse(self, line)
    print(line.strip('\x00\xff\r\n\t'))
