
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
double timeStepSize = 1;
double* mass;
double t = 0;

int NumberOfBodies;
double C = 0.01/3;

double calcDist(double* Pa, double* Pb) {
    double distance = sqrt(
        (Pa[0] - Pb[0]) * (Pa[0] - Pb[0]) +
        (Pa[1] - Pb[1]) * (Pa[1] - Pb[1]) +
        (Pa[2] - Pb[2]) * (Pa[2] - Pb[2])  
    );
    return distance;
}

void calcForce(int N,int M,  double* Pa, double* Pb, double* fx, double* fy, double* fz) {
    //calculate the actual distance between N and M
    double distance = calcDist(Pa, Pb);
    minDx = std::min(minDx, distance);
    //calculate the force components along x, y, z axis.
    *fx = (Pa[0] - Pb[0]) * mass[N] * mass[M] / distance / distance / distance; 
    *fy = (Pa[1] - Pb[1]) * mass[N] * mass[M] / distance / distance / distance;
    *fz = (Pa[2] - Pb[2]) * mass[N] * mass[M] / distance / distance / distance;
    


	double dis = Pa[0];
	printf("%d %d Hello, %f \n", N, M, dis);
}

void calcVel(int n, int m, double* vx, double* vy, double* vz) {
    //calc v
    *vx = (mass[n] * v[n][0])/(mass[n]+mass[m]) + (mass[m]*v[m][0]/(mass[n]+mass[m]));
    *vy = (mass[n] * v[n][1])/(mass[n]+mass[m]) + (mass[m]*v[m][1]/(mass[n]+mass[m]));
    *vz = (mass[n] * v[n][2])/(mass[n]+mass[m]) + (mass[m]*v[m][2]/(mass[n]+mass[m]));
}






void updateBody() {
  maxV   = 0.0;
  minDx  = std::numeric_limits<double>::max();
  double maxMass = 0;
  for (int m=0; m<NumberOfBodies;m++) {
      maxMass = std::max(maxMass, mass[m]);
  }

  // forcex = force along x direction
  // forcey = force along y direction
  // forcez = force along z direction
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
            //send to calc forces and minDx
            calcForce(n,m, x[n], x[m], &Gx, &Gy, &Gz);

            //Add forces to pair, but negate from the other.
            forcex[n] += Gx; forcex[m] -= Gx;
            forcey[n] += Gy; forcey[m] -= Gy;
            forcez[n] += Gz; forcez[m] -= Gz;

            printf("force: %f %f\n", forcex[n], Gx); 

        }
    }

//Iterate thru all and update particle pos based on prev. velocity, then compute new velocities
    for (int i=0; i<NumberOfBodies; i++) {
        double inc = timeStepSize * v[i][1];
        printf("start: %f, increment: %f, vel: %f,  ", x[i][1], inc, v[i][1]);
        x[i][0] += timeStepSize * v[i][0];
        x[i][1] += timeStepSize * v[i][1];
        x[i][2] += timeStepSize * v[i][2];
        v[i][0] += timeStepSize * forcex[i] / mass[i];
        v[i][1] += timeStepSize * forcey[i] / mass[i];
        v[i][2] += timeStepSize * forcez[i] / mass[i];

        
        printf("end: %f, ", x[i][1]);
        printf("speed: %f\n", v[i][2]);
    }
//check for collisions, reduce number of bodies, maintain integrity of arrays.
if (minDx < C*2*maxMass) {
    for (int n=0; n<NumberOfBodies-1; n++) {
        for (int m=n+1; m<NumberOfBodies; m++) {
            double distance = calcDist(x[n], x[m]);
            //check distance is less than C times mass
            if (distance <= C * (mass[m]+mass[n])) {
                //collide
                double vx, vy, vz;
                calcVel(n, m, &vx, &vy, &vz);
                //smaller index becomes the aggregate, then final element in list becomes second element
                v[n][0] = vx; v[n][1] = vy; v[n][2] = vz;
                mass[n] = mass[m] + mass[n];
                x[n][0] = (x[n][0] + x[m][0]) /2;
                x[n][1] = (x[n][1] + x[m][1]) /2;
                x[n][2] = (x[n][2] + x[m][2]) /2;
                //re allocate within memory, move final body into 'm' position
                v[m] = v[NumberOfBodies];
                mass[m] = mass[NumberOfBodies];
                x[m] = x[NumberOfBodies];
                //reduce Number of Bodies by 1
                NumberOfBodies -= 1;
            }
        }
    }
}



//ending adjustment
maxV = 0;
double tempV = 0;
for (int i=0; i<NumberOfBodies; i++) {
    tempV += v[i][0] * v[i][0] + v[i][1] * v[i][1] + v[i][2] * v[i][2];
    maxV = std::max(std::sqrt(tempV), maxV);
}
    t += timeStepSize;
    printf("time:  %f,   \n", t);

    delete[] forcex;
    delete[] forcey;
    delete[] forcez;
    printf("maxV: %f,  minDx: %f \n", maxV, minDx);
}






int main() {
    
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
    x[0][0] = 10;
	x[0][1] = 0;
	x[0][2] = 0;
    x[1][0] = 11;
	x[1][1] = 0;
	x[1][2] = 0;
	x[2][0] = 0;
    x[2][1] = 50;
	x[2][2] = 0;



    while (t< T) {
        updateBody();
	printf("Byeeee\n\n");
    }
}
