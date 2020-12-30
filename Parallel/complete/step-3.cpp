// Translate this file with
//
// g++ -O3 assignment-code.cpp -o assignment-code
//
// Run it with
//
// ./demo-code
//
// There should be a result.pvd file that you can open with Paraview.
// Sometimes, Paraview requires to select the representation "Point Gaussian"
// to see something meaningful.
//
// (C) 2018-2019 Tobias Weinzierl

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

/**
 * Set up scenario from the command line.
 *
 * This operation is not to be changed in the assignment.
 */
void setUp(int argc, char **argv)
{
    NumberOfBodies = (argc - 4) / 7;

    x = new double *[NumberOfBodies];
    v = new double *[NumberOfBodies];
    mass = new double[NumberOfBodies];

    int readArgument = 1;

    tPlotDelta = std::stof(argv[readArgument]);
    readArgument++;
    tFinal = std::stof(argv[readArgument]);
    readArgument++;
    timeStepSize = std::stof(argv[readArgument]);
    readArgument++;

    for (int i = 0; i < NumberOfBodies; i++)
    {
        x[i] = new double[3];
        v[i] = new double[3];

        x[i][0] = std::stof(argv[readArgument]);
        readArgument++;
        x[i][1] = std::stof(argv[readArgument]);
        readArgument++;
        x[i][2] = std::stof(argv[readArgument]);
        readArgument++;

        v[i][0] = std::stof(argv[readArgument]);
        readArgument++;
        v[i][1] = std::stof(argv[readArgument]);
        readArgument++;
        v[i][2] = std::stof(argv[readArgument]);
        readArgument++;

        mass[i] = std::stof(argv[readArgument]);
        readArgument++;

        if (mass[i] <= 0.0)
        {
            std::cerr << "invalid mass for body " << i << std::endl;
            exit(-2);
        }
    }

    std::cout << "created setup with " << NumberOfBodies << " bodies" << std::endl;

    if (tPlotDelta <= 0.0)
    {
        std::cout << "plotting switched off" << std::endl;
        tPlot = tFinal + 1.0;
    }
    else
    {
        std::cout << "plot initial setup plus every " << tPlotDelta << " time units" << std::endl;
        tPlot = 0.0;
    }
}

std::ofstream videoFile;

/**
 * This operation is not to be changed in the assignment.
 */
void openParaviewVideoFile()
{
    videoFile.open("result.pvd");
    videoFile << "<?xml version=\"1.0\"?>" << std::endl
              << "<VTKFile type=\"Collection\" version=\"0.1\" byte_order=\"LittleEndian\" compressor=\"vtkZLibDataCompressor\">" << std::endl
              << "<Collection>";
}

/**
 * This operation is not to be changed in the assignment.
 */
void closeParaviewVideoFile()
{
    videoFile << "</Collection>"
              << "</VTKFile>" << std::endl;
}

/**
 * The file format is documented at http://www.vtk.org/wp-content/uploads/2015/04/file-formats.pdf
 *
 * This operation is not to be changed in the assignment.
 */
void printParaviewSnapshot()
{
    static int counter = -1;
    counter++;
    std::stringstream filename;
    filename << "result-" << counter << ".vtp";
    std::ofstream out(filename.str().c_str());
    out << "<VTKFile type=\"PolyData\" >" << std::endl
        << "<PolyData>" << std::endl
        << " <Piece NumberOfPoints=\"" << NumberOfBodies << "\">" << std::endl
        << "  <Points>" << std::endl
        << "   <DataArray type=\"Float64\" NumberOfComponents=\"3\" format=\"ascii\">";
    //      << "   <DataArray type=\"Float32\" NumberOfComponents=\"3\" format=\"ascii\">";

    for (int i = 0; i < NumberOfBodies; i++)
    {
        out << x[i][0]
            << " "
            << x[i][1]
            << " "
            << x[i][2]
            << " ";
    }

    out << "   </DataArray>" << std::endl
        << "  </Points>" << std::endl
        << " </Piece>" << std::endl
        << "</PolyData>" << std::endl
        << "</VTKFile>" << std::endl;

    videoFile << "<DataSet timestep=\"" << counter << "\" group=\"\" part=\"0\" file=\"" << filename.str() << "\"/>" << std::endl;
}

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

/**
 * This is the only operation you are allowed to change in the assignment.
 * update to include rk2
 */
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

/**
 * Main routine.
 *
 * Not to be changed in assignment.
 */
int main(int argc, char **argv)
{
    if (argc == 1)
    {
        std::cerr << "usage: " + std::string(argv[0]) + " snapshot final-time dt objects" << std::endl
                  << "  snapshot        interval after how many time units to plot. Use 0 to switch off plotting" << std::endl
                  << "  final-time      simulated time (greater 0)" << std::endl
                  << "  dt              time step size (greater 0)" << std::endl
                  << std::endl
                  << "Examples:" << std::endl
                  << "0.01  100.0  0.001    0.0 0.0 0.0  1.0 0.0 0.0  1.0 \t One body moving form the coordinate system's centre along x axis with speed 1" << std::endl
                  << "0.01  100.0  0.001    0.0 0.0 0.0  1.0 0.0 0.0  1.0     0.0 1.0 0.0  1.0 0.0 0.0  1.0  \t One spiralling around the other one" << std::endl
                  << "0.01  100.0  0.001    3.0 0.0 0.0  0.0 1.0 0.0  0.4     0.0 0.0 0.0  0.0 0.0 0.0  0.2     2.0 0.0 0.0  0.0 0.0 0.0  1.0 \t Three body setup from first lecture" << std::endl
                  << "0.01  100.0  0.001    3.0 0.0 0.0  0.0 1.0 0.0  0.4     0.0 0.0 0.0  0.0 0.0 0.0  0.2     2.0 0.0 0.0  0.0 0.0 0.0  1.0     2.0 1.0 0.0  0.0 0.0 0.0  1.0     2.0 0.0 1.0  0.0 0.0 0.0  1.0 \t Five body setup" << std::endl
                  << std::endl
                  << "In this naive code, only the first body moves" << std::endl;

        return -1;
    }
    else if ((argc - 4) % 7 != 0)
    {
        std::cerr << "error in arguments: each planet is given by seven entries (position, velocity, mass)" << std::endl;
        std::cerr << "got " << argc << " arguments (three of them are reserved)" << std::endl;
        std::cerr << "run without arguments for usage instruction" << std::endl;
        return -2;
    }

    std::cout << std::setprecision(15);

    setUp(argc, argv);

    openParaviewVideoFile();

    int snapshotCounter = 0;
    if (t > tPlot)
    {
        printParaviewSnapshot();
        std::cout << "plotted initial setup" << std::endl;
        tPlot = tPlotDelta;
    }

    int timeStepCounter = 0;
    while (t <= tFinal)
    {
        updateBody();
        timeStepCounter++;
        if (t >= tPlot)
        {
            printParaviewSnapshot();
            std::cout << "plot next snapshot"
                      << ",\t time step=" << timeStepCounter
                      << ",\t t=" << t
                      << ",\t dt=" << timeStepSize
                      << ",\t v_max=" << maxV
                      << ",\t dx_min=" << minDx
                      << std::endl;

            tPlot += tPlotDelta;
        }
    }

    std::cout << "Number of remaining objects: " << NumberOfBodies << std::endl;
    std::cout << "Position of first remaining object: " << x[0][0] << ", " << x[0][1] << ", " << x[0][2] << std::endl;

    closeParaviewVideoFile();

    return 0;
}