// Simple demonstration to get the data out of a measurement set

#include <iostream>
#include <casacore/casa/aips.h>
#include <casacore/casa/Arrays/Cube.h>
#include <casacore/tables/Tables/TableIter.h>
#include <casacore/tables/Tables/ScalarColumn.h>
#include <casacore/tables/Tables/ArrayColumn.h>

using namespace std;
using namespace casa;

void printuvw(double *data, int nbl) {
  for (int bl=0; bl<nbl; ++bl) {
    cout<<"uvw["<<bl<<"]=["<<data[3*bl]<<", "<<data[3*bl+1]<<", "<<data[3*bl+2]<<"]"<<endl;
  }
}

void printdata(Complex *data, bool *flag, int ncr, int nch, int nbl) {
  for (int bl=0; bl<nbl; ++bl) {
    for (int ch=0; ch<nch; ++ch) {
      for (int cr=0; cr<ncr; ++cr) {
        cout<<"data["<<bl<<","<<ch<<","<<cr<<"] = "<<data[ ncr*nch*bl +ncr*ch + cr];
        if (flag[ ncr*nch*bl +ncr*ch + cr]) {
          cout<<" (flagged)";
        }
        cout<<endl;
      }
    }
  }
}


int main() {
  Table tim("tim.MS");

  // Get iterator for column TIME, so for each iteration we get all baselines at that time
  TableIterator iter(tim, Block<String>(1, "TIME"), TableIterator::Ascending, TableIterator::NoSort);

  // Number of rows in one iteration, so number of baselines
  int nbl = iter.table().nrow();
  cout << "Number of baselines: " << nbl << endl;
  int ncr = 4; // Number of correlations: xx, xy, yx, yy
  
  // Read frequencies
  Table timch("tim.MS/SPECTRAL_WINDOW");
  ArrayColumn<double> chancol(timch, "CHAN_FREQ");
  Matrix<double> chanfreqs = chancol.getColumn();
  int nch = chanfreqs.nelements(); // Number of channels
  cout<<"Number of channels: "<<nch<<endl;

  // Print channels
  for (int i=0; i<nch; ++i) {
    cout << chanfreqs(i, 0) << endl;
  }

  ScalarColumn<Int> ant1col(iter.table(), "ANTENNA1");
  ScalarColumn<Int> ant2col(iter.table(), "ANTENNA2"); 

  Vector<int> ant1 = ant1col.getColumn();
  Vector<int> ant2 = ant2col.getColumn();

  Cube<Complex> data(ncr, nch, nbl);
  Matrix<double> uvw(3, nbl);
  Cube<Bool> flag(ncr, nch, nbl);

  // Print antenna numbers
  for (int i=0; i<ant1.size(); ++i) {
    cout << ant1[i] << ", " << ant2[i]<<endl;
  }

  // Read data
  while (!iter.pastEnd()) {
    ScalarColumn<double> timecol(iter.table(), "TIME");
    cout<<"Time: "<<timecol.getColumn()(0)<<endl;
    ArrayColumn<Complex> datacol(iter.table(), "DATA");
    ArrayColumn<Double> uvwcol(iter.table(), "UVW");
    ArrayColumn<bool> flagcol(iter.table(), "FLAG");
    datacol.getColumn(data);
    uvwcol.getColumn(uvw);
    flagcol.getColumn(flag);
    printdata(data.data(), flag.data(), ncr, nch, nbl);
    printuvw(uvw.data(), nbl);
    iter.next();
  } 
}
