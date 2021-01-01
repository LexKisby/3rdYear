#include <fstream>
#include <sstream>
#include <iostream>
#include <string>
#include <math.h>
#include <limits>
#include <iomanip>

#include <cmath>

double t = 0;
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

void updateBody()
////This implementation runs on the basis that the supplied velocity and position are correct and do not need to be
////adjusted by forces before use, i.e v = hf(tn, yn)
{
    //////////////////////////////////////////////////////
    //Init values
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

    ////////////////////////////////////////////////////////
    //generate intermediate positions at half timestep
    double **tempX;
    double **tempV;
    tempX = new double *[NumberOfBodies];
    tempV = new double *[NumberOfBodies];
#pragma omp simd
    for (int i = 0; i < NumberOfBodies; i++)
    {
        tempX[i] = new double[3];
        tempV[i] = new double[3];

        tempX[i][0] = x[i][0] + timeStepSize * v[i][0] * 0.5;
        tempX[i][1] = x[i][1] + timeStepSize * v[i][1] * 0.5;
        tempX[i][2] = x[i][2] + timeStepSize * v[i][2] * 0.5;

        //init forces
        forcex[i] = 0.0;
        forcey[i] = 0.0;
        forcez[i] = 0.0;
    }

    //////////////////////////////////////////////////////////////
    //generate intermediate force from tempX
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

            forcex[n] -= Gx;
            forcex[m] += Gx;
            forcey[n] -= Gy;
            forcey[m] += Gy;
            forcez[n] -= Gz;
            forcez[m] += Gz;
        }
    }

//////////////////////////////////////////////////////////////////
//generate intermediate velocity from supplied velocity and intermediate force
#pragma omp simd
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

    ///////////////////////////////////////////////////////////////////////////
    //generate new force from new pos
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

            forcex[n] -= Gx;
            forcex[m] += Gx;
            forcey[n] -= Gy;
            forcey[m] += Gy;
            forcez[n] -= Gz;
            forcez[m] += Gz;
        }
    }

    ////////////////////////////////////////////////////////////////////////
    //generate new velocity from new force and original velocity
    for (int i = 0; i < NumberOfBodies; i++)
    {
        v[i][0] += timeStepSize * forcex[i] / mass[i];
        v[i][1] += timeStepSize * forcey[i] / mass[i];
        v[i][2] += timeStepSize * forcez[i] / mass[i];
    }

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

//////////////////////////////////////////////////
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
#pragma omp simd reduction(max \
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