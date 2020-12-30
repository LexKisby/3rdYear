#include <cmath>
#include <fstream>
#include <sstream>
#include <iostream>
#include <string>
#include <math.h>
#include <limits>
#include <iomanip>

double C;
double maxV;
double minDx;
double maxMass;
int NumberOfBodies;
double **x;
double t = 0;

/**
 * Equivalent to x storing the velocities.
 */
double **v;

/**
 * One mass entry per molecule/particle.
 */
double *mass;

/**
 * Global time step size used.
 */
double timeStepSize = 0.0;

double calcDist(double *Pa, double *Pb)
{
    double distance = sqrt(
        (Pa[0] - Pb[0]) * (Pa[0] - Pb[0]) +
        (Pa[1] - Pb[1]) * (Pa[1] - Pb[1]) +
        (Pa[2] - Pb[2]) * (Pa[2] - Pb[2]));
    return distance;
}

//this is no longer used
void calcForce(int N, int M, double *Pa, double *Pb, double *fx, double *fy, double *fz)
{
    //calculate the actual distance between N and M
    double distance = calcDist(Pa, Pb);
    minDx = std::min(minDx, distance);
    //calculate the force components along x, y, z axis.
    *fx = (Pa[0] - Pb[0]) * mass[N] * mass[M] / distance / distance / distance;
    *fy = (Pa[1] - Pb[1]) * mass[N] * mass[M] / distance / distance / distance;
    *fz = (Pa[2] - Pb[2]) * mass[N] * mass[M] / distance / distance / distance;
}
void calcVel(int n, int m, double *vx, double *vy, double *vz)
{
    //calc v
    *vx = (mass[n] * v[n][0]) / (mass[n] + mass[m]) + (mass[m] * v[m][0] / (mass[n] + mass[m]));
    *vy = (mass[n] * v[n][1]) / (mass[n] + mass[m]) + (mass[m] * v[m][1] / (mass[n] + mass[m]));
    *vz = (mass[n] * v[n][2]) / (mass[n] + mass[m]) + (mass[m] * v[m][2] / (mass[n] + mass[m]));
}

void updateBody()
{
    C = 0.01 / NumberOfBodies;
    maxV = 0.0;
    minDx = std::numeric_limits<double>::max();
    double maxMass = 0;
    for (int m = 0; m < NumberOfBodies; m++)
    {
        maxMass = std::max(maxMass, mass[m]);
    }

    // forcex = force along x direction
    // forcey = force along y direction
    // forcez = force along z direction
    //generate pointers to lists so each body has a force
    double *forcex = new double[NumberOfBodies];
    double *forcey = new double[NumberOfBodies];
    double *forcez = new double[NumberOfBodies];

    //All forces initialised to 0 for all bodies
    for (int i = 0; i < NumberOfBodies; i++)
    {
        forcex[i] = 0.0;
        forcey[i] = 0.0;
        forcez[i] = 0.0;
    }

    //Iterate through all pairs of bodies and use symmetry to assign force to both bodies
    //calculates the force based on current position, then will update position based on previously calculted velocity
    for (int n = 0; n < NumberOfBodies - 1; n++)
    {
#pragma omp simd reduction(min \
                           : minDx)
        for (int m = n + 1; m < NumberOfBodies; m++)
        {
            double Gx, Gy, Gz;
            //calculate the actual distance between N and M
            double distance = sqrt(
                (x[n][0] - x[m][0]) * (x[n][0] - x[m][0]) +
                (x[n][1] - x[m][1]) * (x[n][1] - x[m][1]) +
                (x[n][2] - x[m][2]) * (x[n][2] - x[m][2]));

            minDx = std::min(minDx, distance);
            //calculate the force components along x, y, z axis.
            Gx = (x[n][0] - x[m][0]) * mass[n] * mass[m] / distance / distance / distance;
            Gy = (x[n][1] - x[m][1]) * mass[n] * mass[m] / distance / distance / distance;
            Gz = (x[n][2] - x[m][2]) * mass[n] * mass[m] / distance / distance / distance;

            //Add forces to pair, but negate from the other.
            //force has direction so getting the right way is important
            forcex[n] -= Gx;
            forcex[m] += Gx;
            forcey[n] -= Gy;
            forcey[m] += Gy;
            forcez[n] -= Gz;
            forcez[m] += Gz;
        }
    }

//Iterate thru all and update particle pos based on prev. velocity, then compute new velocities to be applied next time step
#pragma omp simd
    for (int i = 0; i < NumberOfBodies; i++)
    {
        x[i][0] += timeStepSize * v[i][0];
        x[i][1] += timeStepSize * v[i][1];
        x[i][2] += timeStepSize * v[i][2];
        //calc new velocities
        v[i][0] += timeStepSize * forcex[i] / mass[i];
        v[i][1] += timeStepSize * forcey[i] / mass[i];
        v[i][2] += timeStepSize * forcez[i] / mass[i];
    }

    //check for collisions, reduce number of bodies, maintain integrity of arrays.
    //basic bottleneck test, from minDx calculated in the force calcualtions
    //if the min distance is greater than the constraint for the largest mass item in the system , then no collisions have occurred.
    if (minDx <= C * 2 * maxMass)
    {
        //otherwise check every item
        for (int n = 0; n < NumberOfBodies - 1; n++)
        {
            for (int m = n + 1; m < NumberOfBodies; m++)
            {
                if (m > NumberOfBodies - 1)
                {
                }
                else
                {
                    double distance = calcDist(x[n], x[m]);
                    //check distance is less than C times mass
                    if (distance <= C * (mass[m] + mass[n]))
                    {
                        //collide
                        double vx, vy, vz;
                        calcVel(n, m, &vx, &vy, &vz);
                        //smaller index becomes the aggregate, then final element in list becomes second element
                        v[n][0] = vx;
                        v[n][1] = vy;
                        v[n][2] = vz;
                        //avg position with mass weighting
                        x[n][0] = (x[n][0] * mass[n] + x[m][0] * mass[m]) / (mass[n] + mass[m]);
                        x[n][1] = (x[n][1] * mass[n] + x[m][1] * mass[m]) / (mass[n] + mass[m]);
                        x[n][2] = (x[n][2] * mass[n] + x[m][2] * mass[m]) / (mass[n] + mass[m]);
                        //sum mass
                        mass[n] = mass[m] + mass[n];
                        //re allocate within memory, move final body into 'm' position
                        v[m] = v[NumberOfBodies - 1];
                        mass[m] = mass[NumberOfBodies - 1];
                        x[m] = x[NumberOfBodies - 1];

                        //reduce Number of Bodies by 1 so
                        NumberOfBodies -= 1;
                    }
                }
            }
        }
    }

    //ending adjustment to find max velocity
    maxV = 0;
#pragma omp simd reduction(max \
                           : maxV)
    for (int i = 0; i < NumberOfBodies; i++)
    {
        double tempV = v[i][0] * v[i][0] + v[i][1] * v[i][1] + v[i][2] * v[i][2];
        maxV = std::max(std::sqrt(tempV), maxV);
    }
    t += timeStepSize;

    delete[] forcex;
    delete[] forcey;
    delete[] forcez;
}

int main()
{
    updateBody();
    return 1;
}