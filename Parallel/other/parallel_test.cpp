
#include <fstream>
#include <sstream>
#include <iostream>
#include <string>
#include <math.h>
#include <limits>
#include <iomanip>

#include <cmath>
#include "omp.h"

double t = 0.0;
double tFinal = 0;
double tPlot = 0;
double tPlotDelta = 0;

int NumberOfBodies = 0;
double C;

/**
 * Pointer to pointers. Each pointer in turn points to three coordinates, i.e.
 * each pointer represents one molecule/particle/body.
 */
double **x;

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

/**
 * Maximum velocity of all particles.
 */
double maxV;

/**
 * Minimum distance between two elements.
 */
double minDx;

double calcDist(double *Pa, double *Pb)
{
    double distance = sqrt(
        (Pa[0] - Pb[0]) * (Pa[0] - Pb[0]) +
        (Pa[1] - Pb[1]) * (Pa[1] - Pb[1]) +
        (Pa[2] - Pb[2]) * (Pa[2] - Pb[2]));
    return distance;
}

void calcVel(int n, int m, double *vx, double *vy, double *vz)
{
    //calc v
    *vx = (mass[n] * v[n][0]) / (mass[n] + mass[m]) + (mass[m] * v[m][0] / (mass[n] + mass[m]));
    *vy = (mass[n] * v[n][1]) / (mass[n] + mass[m]) + (mass[m] * v[m][1] / (mass[n] + mass[m]));
    *vz = (mass[n] * v[n][2]) / (mass[n] + mass[m]) + (mass[m] * v[m][2] / (mass[n] + mass[m]));
}

//////////////////////////////////////////////////////////////////////////////
void updateBody()
{

    C = 0.01 / NumberOfBodies;
    maxV = 0.0;
    minDx = std::numeric_limits<double>::max();
    double maxMass = 0;
#pragma omp simd reduction(max \
                           : maxMass)
    for (int m = 0; m < NumberOfBodies; m++)
    {
        maxMass = std::max(maxMass, mass[m]);
    }

    double *forcex = new double[NumberOfBodies];
    double *forcey = new double[NumberOfBodies];
    double *forcez = new double[NumberOfBodies];

    double **tempX;
    double **tempV;
    tempX = new double *[NumberOfBodies];
    tempV = new double *[NumberOfBodies];

    omp_set_num_threads(4);
    //\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/

#pragma omp parallel
    {
        //decided to not extract into functions
        int ID = omp_get_thread_num();
        int nthrds = omp_get_num_threads();

#pragma omp simd
        for (int i = ID; i < NumberOfBodies; i += nthrds)
        {
            tempX[i] = new double[3];
            tempV[i] = new double[3];

            //temp positions
            tempX[i][0] = x[i][0] + timeStepSize * v[i][0] * 0.5;
            tempX[i][1] = x[i][1] + timeStepSize * v[i][1] * 0.5;
            tempX[i][2] = x[i][2] + timeStepSize * v[i][2] * 0.5;

            //init forces
            forcex[i] = 0.0;
            forcey[i] = 0.0;
            forcez[i] = 0.0;
        }
    }
// force from temp pos
#pragma omp parallel
    {
#pragma omp for
        for (int n = 0; n < NumberOfBodies - 1; n++)
        {
#pragma omp simd
            for (int m = n + 1; m < NumberOfBodies; m++)
            {
                double Gx, Gy, Gz;
                double distance = sqrt(
                    (tempX[n][0] - tempX[m][0]) * (tempX[n][0] - tempX[m][0]) +
                    (tempX[n][1] - tempX[m][1]) * (tempX[n][1] - tempX[m][1]) +
                    (tempX[n][2] - tempX[m][2]) * (tempX[n][2] - tempX[m][2]));

                Gx = (tempX[n][0] - tempX[m][0]) * mass[n] * mass[m] / distance / distance / distance;
                Gy = (tempX[n][1] - tempX[m][1]) * mass[n] * mass[m] / distance / distance / distance;
                Gz = (tempX[n][2] - tempX[m][2]) * mass[n] * mass[m] / distance / distance / distance;

#pragma omp atomic
                forcex[n] -= Gx;
#pragma omp atomic
                forcex[m] += Gx;
#pragma omp atomic
                forcey[n] -= Gy;
#pragma omp atomic
                forcey[m] += Gy;
#pragma omp atomic
                forcez[n] -= Gz;
#pragma omp atomic
                forcez[m] += Gz;
            }
        }
    }
    //generate velocities from original v and calculated force
#pragma omp parallel for
    for (int i = 0; i < NumberOfBodies; i++)
    {
        tempV[i][0] = v[i][0] + timeStepSize * forcex[i] / mass[i];
        tempV[i][1] = v[i][1] + timeStepSize * forcey[i] / mass[i];
        tempV[i][2] = v[i][2] + timeStepSize * forcez[i] / mass[i];

        forcex[i] = 0.0;
        forcey[i] = 0.0;
        forcez[i] = 0.0;

        //////////////////////////////////////////////////////////////////
        //apply intermediate velocity to supplied position as full timestep
        x[i][0] += timeStepSize * tempV[i][0];
        x[i][1] += timeStepSize * tempV[i][1];
        x[i][2] += timeStepSize * tempV[i][2];
    }

#pragma omp parallel
    {
#pragma omp for
        for (int n = 0; n < NumberOfBodies - 1; n++)
        {
#pragma omp simd reduction(min \
                           : minDx)
            for (int m = n + 1; m < NumberOfBodies; m++)
            {
                double Gx, Gy, Gz;
                double distance = sqrt(
                    (x[n][0] - x[m][0]) * (x[n][0] - x[m][0]) +
                    (x[n][1] - x[m][1]) * (x[n][1] - x[m][1]) +
                    (x[n][2] - x[m][2]) * (x[n][2] - x[m][2]));

                minDx = std::min(minDx, distance);

                Gx = (x[n][0] - x[m][0]) * mass[n] * mass[m] / distance / distance / distance;
                Gy = (x[n][1] - x[m][1]) * mass[n] * mass[m] / distance / distance / distance;
                Gz = (x[n][2] - x[m][2]) * mass[n] * mass[m] / distance / distance / distance;

#pragma omp atomic
                forcex[n] -= Gx;
#pragma omp atomic
                forcex[m] += Gx;
#pragma omp atomic
                forcey[n] -= Gy;
#pragma omp atomic
                forcey[m] += Gy;
#pragma omp atomic
                forcez[n] -= Gz;
#pragma omp atomic
                forcez[m] += Gz;
            }
        }
    }
#pragma omp parallel for
    for (int i = 0; i < NumberOfBodies; i++)
    {
        v[i][0] += timeStepSize * forcex[i] / mass[i];
        v[i][1] += timeStepSize * forcey[i] / mass[i];
        v[i][2] += timeStepSize * forcez[i] / mass[i];
    }
    //\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
    //parallel over
    //////////////////////////////////////////////////////////////////////////
    //detect collisions
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
//final inits
#pragma omp simd
    for (int i = 0; i < NumberOfBodies; i++)
    {
        delete[] tempX[i];
        delete[] tempV[i];
    }
    delete[] tempX;
    delete[] tempV;

    maxV = 0;

#pragma omp parallel for reduction(max \
                                   : maxV)
    for (int i = 0; i < NumberOfBodies; i++)
    {
        double notV = v[i][0] * v[i][0] + v[i][1] * v[i][1] + v[i][2] * v[i][2];
        maxV = std::max(std::sqrt(notV), maxV);
    }

    t += timeStepSize;

    delete[] forcex;
    delete[] forcey;
    delete[] forcez;
}

////////////////////////////////////////////////////////
int main()
{

    updateBody();
    return 0;
}