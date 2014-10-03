#include <string>

// This file will be formatted too

class Test
{
public:

  virtual Test *getChildTestAt( int index ) const;



  virtual std::string getName(  ) const =0;


  virtual bool findTestPath( const std::string &testName,
                             TestPath &testPath ) const;
};

