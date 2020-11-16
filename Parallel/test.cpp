
#include <fstream>
#include <sstream>
#include <iostream>
#include <string>
#include <math.h>
#include <limits>
#include <iomanip>

#include <cmath>



double maxV = 0;
double minDx = 100;
double** x;
double** v;
double timeStepSize = 0.1;
double* mass;

int NumberOfBodies;


void calcForce(int N,int m,  double* Pa, double* Pb, double* fx, double* fy, double* fz) {
    *fx = 5;
    *fy = 5;
    *fz = 5;
	double dis = Pa[0];
	printf("%d %d Hello, %f \n",N,m, dis);
}







void updateBody() {
  maxV   = 0.0;
  minDx  = std::numeric_limits<double>::max();

  // force0 = force along x direction
  // force1 = force along y direction
  // force2 = force along z direction
  //generate pointers to lists so each body has a force
  double* forcex = new double[NumberOfBodies];
  double* forcey = new double[NumberOfBodies];
  double* forcez = new double[NumberOfBodies];

  //All forces initialised to 0
  for (int i=0; i<NumberOfBodies; i++) {
  forcex[i] = 0.0;
  forcey[i] = 0.0;
  forcez[i] = 0.0;
  }
//Iterate through all pairs of bodies and use symmetry to assign force to both bodies
    for (int n=0; n<NumberOfBodies-1; n++) {
        for (int m=n+1; m<NumberOfBodies; m++) {
            double Gx, Gy, Gz;

            //need to calc distances

            calcForce(n,m, x[n], x[m], &Gx, &Gy, &Gz);
            //needs more stuffs

            //Add forces to pair
            forcex[n] += Gx; forcex[m] += Gx;
		printf("force: %f %f\n", forcex[n], Gx); 
            forcey[n] += Gy; forcey[m] += Gy;
            forcez[n] += Gz; forcez[m] += Gz;

        }
    }

//Iterate thru all and update particle pos based on prev. velocity, then compute new velocities
    for (int i=0; i<NumberOfBodies; i++) {
        x[i][0] += timeStepSize * v[i][0];
	double inc = timeStepSize * v[i][0];
	printf("start: %f, increment: %f, vel: %f,  ", x[i][1], inc, v[i][1]);
        x[i][1] += timeStepSize * v[i][1];
	printf("end: %f, ", x[i][1]);
        x[i][2] += timeStepSize * v[i][2];
        v[i][0] += timeStepSize * forcex[i] / mass[i];
        v[i][1] += timeStepSize * forcey[i] / mass[i];
        v[i][2] += timeStepSize * forcez[i] / mass[i];
printf("speed: %f\n", v[i][2]);
    }
//check for collisions, reduce number of bodies, maintain integrity of arrays.
}

int main() {
    int t = 0;
    int T = 5;
    NumberOfBodies = 3;
    x    = new double*[NumberOfBodies];
    v    = new double*[NumberOfBodies];
    mass = new double [NumberOfBodies];

    for (int i=0; i<NumberOfBodies; i++) {
    x[i] = new double[3];
    v[i] = new double[3];
    mass[i] = 5;
        for (int j=0; j<3; j++) {
            v[i][j] = 0;
        }
    }
//set locations
    x[0][0] = 100;
	x[0][1] = 0;
	x[0][2] = 0;
    x[1][0] = 10;
	x[1][1] = 0;
	x[1][2] = 0;
	x[2][0] = 0;
    x[2][1] = 50;
	x[2][2] = 0;



    while (t++< T) {
        updateBody();
	printf("Byeeee\n\n");
    }
}