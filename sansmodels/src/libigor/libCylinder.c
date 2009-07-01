/*	CylinderFit.c

A simplified project designed to act as a template for your curve fitting function.
The fitting function is a Cylinder form factor. No resolution effects are included (yet)
*/

#include "StandardHeaders.h"			// Include ANSI headers, Mac headers
#include "GaussWeights.h"
#include "libCylinder.h"
/*	CylinderForm  :  calculates the form factor of a cylinder at the give x-value p->x

Warning:
The call to WaveData() below returns a pointer to the middle
of an unlocked Macintosh handle. In the unlikely event that your
calculations could cause memory to move, you should copy the coefficient
values to local variables or an array before such operations.
*/
double
CylinderForm(double dp[], double q)
{
	int i;
	double Pi;
	double scale,radius,length,delrho,bkg,halfheight;		//local variables of coefficient wave
	int nord=76;			//order of integration
	double uplim,lolim;		//upper and lower integration limits
	double summ,zi,yyy,answer,vcyl;			//running tally of integration
	
	Pi = 4.0*atan(1.0);
	lolim = 0;
	uplim = Pi/2.0;
	
	summ = 0.0;			//initialize intergral
	
	scale = dp[0];			//make local copies in case memory moves
	radius = dp[1];
	length = dp[2];
	delrho = dp[3];
	bkg = dp[4];
	halfheight = length/2.0;
	for(i=0;i<nord;i++) {
		zi = ( Gauss76Z[i]*(uplim-lolim) + uplim + lolim )/2.0;
		yyy = Gauss76Wt[i] * CylKernel(q, radius, halfheight, zi);
		summ += yyy;
	}
	
	answer = (uplim-lolim)/2.0*summ;
	// Multiply by contrast^2
	answer *= delrho*delrho;
	//normalize by cylinder volume
	//NOTE that for this (Fournet) definition of the integral, one must MULTIPLY by Vcyl
	vcyl=Pi*radius*radius*length;
	answer *= vcyl;
	//convert to [cm-1]
	answer *= 1.0e8;
	//Scale
	answer *= scale;
	// add in the background
	answer += bkg;
	
	return answer;
}

/*	EllipCyl76X  :  calculates the form factor of a elliptical cylinder at the given x-value p->x

Uses 76 pt Gaussian quadrature for both integrals

Warning:
The call to WaveData() below returns a pointer to the middle
of an unlocked Macintosh handle. In the unlikely event that your
calculations could cause memory to move, you should copy the coefficient
values to local variables or an array before such operations.
*/
double
EllipCyl76(double dp[], double q)
{
	int i,j;
	double Pi;
	double scale,ra,nu,length,delrho,bkg;		//local variables of coefficient wave
	int nord=76;			//order of integration
	double va,vb;		//upper and lower integration limits
	double summ,zi,yyy,answer,vell;			//running tally of integration
	double summj,vaj,vbj,zij,arg;			//for the inner integration
	
	Pi = 4.0*atan(1.0);
	va = 0;
	vb = 1;		//orintational average, outer integral
	vaj=0;
	vbj=Pi;		//endpoints of inner integral
	
	summ = 0.0;			//initialize intergral
	
	scale = dp[0];			//make local copies in case memory moves
	ra = dp[1];
	nu = dp[2];
	length = dp[3];
	delrho = dp[4];
	bkg = dp[5];
	for(i=0;i<nord;i++) {
		//setup inner integral over the ellipsoidal cross-section
		summj=0;
		zi = ( Gauss76Z[i]*(vb-va) + va + vb )/2.0;		//the "x" dummy
		arg = ra*sqrt(1-zi*zi);
		for(j=0;j<nord;j++) {
			//76 gauss points for the inner integral as well
			zij = ( Gauss76Z[j]*(vbj-vaj) + vaj + vbj )/2.0;		//the "y" dummy
			yyy = Gauss76Wt[j] * EllipCylKernel(q,arg,nu,zij);
			summj += yyy;
		}
		//now calculate the value of the inner integral
		answer = (vbj-vaj)/2.0*summj;
		//divide integral by Pi
		answer /=Pi;
		
		//now calculate outer integral
		arg = q*length*zi/2;
		yyy = Gauss76Wt[i] * answer * sin(arg) * sin(arg) / arg / arg;
		summ += yyy;
	}
	answer = (vb-va)/2.0*summ;
	// Multiply by contrast^2
	answer *= delrho*delrho;
	//normalize by cylinder volume
	//NOTE that for this (Fournet) definition of the integral, one must MULTIPLY by Vcyl
	vell = Pi*ra*(nu*ra)*length;
	answer *= vell;
	//convert to [cm-1]
	answer *= 1.0e8;
	//Scale
	answer *= scale;
	// add in the background
	answer += bkg;
	
	return answer;
}

/*	EllipCyl20X  :  calculates the form factor of a elliptical cylinder at the given x-value p->x

Uses 76 pt Gaussian quadrature for orientational integral
Uses 20 pt quadrature for the inner integral over the elliptical cross-section

Warning:
The call to WaveData() below returns a pointer to the middle
of an unlocked Macintosh handle. In the unlikely event that your
calculations could cause memory to move, you should copy the coefficient
values to local variables or an array before such operations.
*/
double
EllipCyl20(double dp[], double q)
{
	int i,j;
	double Pi;
	double scale,ra,nu,length,delrho,bkg;		//local variables of coefficient wave
	int nordi=76;			//order of integration
	int nordj=20;
	double va,vb;		//upper and lower integration limits
	double summ,zi,yyy,answer,vell;			//running tally of integration
	double summj,vaj,vbj,zij,arg;			//for the inner integration
	
	Pi = 4.0*atan(1.0);
	va = 0;
	vb = 1;		//orintational average, outer integral
	vaj=0;
	vbj=Pi;		//endpoints of inner integral
	
	summ = 0.0;			//initialize intergral
	
	scale = dp[0];			//make local copies in case memory moves
	ra = dp[1];
	nu = dp[2];
	length = dp[3];
	delrho = dp[4];
	bkg = dp[5];
	for(i=0;i<nordi;i++) {
		//setup inner integral over the ellipsoidal cross-section
		summj=0;
		zi = ( Gauss76Z[i]*(vb-va) + va + vb )/2.0;		//the "x" dummy
		arg = ra*sqrt(1-zi*zi);
		for(j=0;j<nordj;j++) {
			//20 gauss points for the inner integral
			zij = ( Gauss20Z[j]*(vbj-vaj) + vaj + vbj )/2.0;		//the "y" dummy
			yyy = Gauss20Wt[j] * EllipCylKernel(q,arg,nu,zij);
			summj += yyy;
		}
		//now calculate the value of the inner integral
		answer = (vbj-vaj)/2.0*summj;
		//divide integral by Pi
		answer /=Pi;
		
		//now calculate outer integral
		arg = q*length*zi/2;
		yyy = Gauss76Wt[i] * answer * sin(arg) * sin(arg) / arg / arg;
		summ += yyy;
	}
	
	answer = (vb-va)/2.0*summ;
	// Multiply by contrast^2
	answer *= delrho*delrho;
	//normalize by cylinder volume
	//NOTE that for this (Fournet) definition of the integral, one must MULTIPLY by Vcyl
	vell = Pi*ra*(nu*ra)*length;
	answer *= vell;
	//convert to [cm-1]
	answer *= 1.0e8;
	//Scale
	answer *= scale;
	// add in the background
	answer += bkg;	
	
	return answer;
}

/*	TriaxialEllipsoidX  :  calculates the form factor of a Triaxial Ellipsoid at the given x-value p->x

Uses 76 pt Gaussian quadrature for both integrals

Warning:
The call to WaveData() below returns a pointer to the middle
of an unlocked Macintosh handle. In the unlikely event that your
calculations could cause memory to move, you should copy the coefficient
values to local variables or an array before such operations.
*/
double
TriaxialEllipsoid(double dp[], double q)
{
	int i,j;
	double Pi;
	double scale,aa,bb,cc,delrho,bkg;		//local variables of coefficient wave
	int nordi=76;			//order of integration
	int nordj=76;
	double va,vb;		//upper and lower integration limits
	double summ,zi,yyy,answer;			//running tally of integration
	double summj,vaj,vbj,zij;			//for the inner integration
	
	Pi = 4.0*atan(1.0);
	va = 0;
	vb = 1;		//orintational average, outer integral
	vaj = 0;
	vbj = 1;		//endpoints of inner integral
	
	summ = 0.0;			//initialize intergral
	
	scale = dp[0];			//make local copies in case memory moves
	aa = dp[1];
	bb = dp[2];
	cc = dp[3];
	delrho = dp[4];
	bkg = dp[5];
	for(i=0;i<nordi;i++) {
		//setup inner integral over the ellipsoidal cross-section
		summj=0;
		zi = ( Gauss76Z[i]*(vb-va) + va + vb )/2.0;		//the "x" dummy
		for(j=0;j<nordj;j++) {
			//20 gauss points for the inner integral
			zij = ( Gauss76Z[j]*(vbj-vaj) + vaj + vbj )/2.0;		//the "y" dummy
			yyy = Gauss76Wt[j] * TriaxialKernel(q,aa,bb,cc,zi,zij);
			summj += yyy;
		}
		//now calculate the value of the inner integral
		answer = (vbj-vaj)/2.0*summj;
		
		//now calculate outer integral
		yyy = Gauss76Wt[i] * answer;
		summ += yyy;
	}		//final scaling is done at the end of the function, after the NT_FP64 case
	
	answer = (vb-va)/2.0*summ;
	// Multiply by contrast^2
	answer *= delrho*delrho;
	//normalize by ellipsoid volume
	answer *= 4*Pi/3*aa*bb*cc;
	//convert to [cm-1]
	answer *= 1.0e8;
	//Scale
	answer *= scale;
	// add in the background
	answer += bkg;
	
	return answer;
}

/*	ParallelepipedX  :  calculates the form factor of a Parallelepiped (a rectangular solid)
at the given x-value p->x

Uses 76 pt Gaussian quadrature for both integrals

Warning:
The call to WaveData() below returns a pointer to the middle
of an unlocked Macintosh handle. In the unlikely event that your
calculations could cause memory to move, you should copy the coefficient
values to local variables or an array before such operations.
*/
double
Parallelepiped(double dp[], double q)
{
	int i,j;
	double scale,aa,bb,cc,delrho,bkg;		//local variables of coefficient wave
	int nordi=76;			//order of integration
	int nordj=76;
	double va,vb;		//upper and lower integration limits
	double summ,yyy,answer;			//running tally of integration
	double summj,vaj,vbj;			//for the inner integration
	double mu,mudum,arg,sigma,uu,vol;
	
	
	//	Pi = 4.0*atan(1.0);
	va = 0;
	vb = 1;		//orintational average, outer integral
	vaj = 0;
	vbj = 1;		//endpoints of inner integral
	
	summ = 0.0;			//initialize intergral
	
	scale = dp[0];			//make local copies in case memory moves
	aa = dp[1];
	bb = dp[2];
	cc = dp[3];
	delrho = dp[4];
	bkg = dp[5];
	
	mu = q*bb;
	vol = aa*bb*cc;
	// normalize all WRT bb
	aa = aa/bb;
	cc = cc/bb;
	
	for(i=0;i<nordi;i++) {
		//setup inner integral over the ellipsoidal cross-section
		summj=0;
		sigma = ( Gauss76Z[i]*(vb-va) + va + vb )/2.0;		//the outer dummy
		
		for(j=0;j<nordj;j++) {
			//76 gauss points for the inner integral
			uu = ( Gauss76Z[j]*(vbj-vaj) + vaj + vbj )/2.0;		//the inner dummy
			mudum = mu*sqrt(1-sigma*sigma);
			yyy = Gauss76Wt[j] * PPKernel(aa,mudum,uu);
			summj += yyy;
		}
		//now calculate the value of the inner integral
		answer = (vbj-vaj)/2.0*summj;
		
		arg = mu*cc*sigma/2;
		if ( arg == 0 ) {
			answer *= 1;
		} else {
			answer *= sin(arg)*sin(arg)/arg/arg;
		}
		
		//now sum up the outer integral
		yyy = Gauss76Wt[i] * answer;
		summ += yyy;
	}		//final scaling is done at the end of the function, after the NT_FP64 case
	
	answer = (vb-va)/2.0*summ;
	// Multiply by contrast^2
	answer *= delrho*delrho;
	//normalize by volume
	answer *= vol;
	//convert to [cm-1]
	answer *= 1.0e8;
	//Scale
	answer *= scale;
	// add in the background
	answer += bkg;
	
	return answer;
}

/*	HollowCylinderX  :  calculates the form factor of a Hollow Cylinder
at the given x-value p->x

Uses 76 pt Gaussian quadrature for the single integral

Warning:
The call to WaveData() below returns a pointer to the middle
of an unlocked Macintosh handle. In the unlikely event that your
calculations could cause memory to move, you should copy the coefficient
values to local variables or an array before such operations.
*/
double
HollowCylinder(double dp[], double q)
{
	int i;
	double scale,rcore,rshell,length,delrho,bkg;		//local variables of coefficient wave
	int nord=76;			//order of integration
	double va,vb,zi;		//upper and lower integration limits
	double summ,answer,pi;			//running tally of integration
	
	pi = 4.0*atan(1.0);
	va = 0;
	vb = 1;		//limits of numerical integral
	
	summ = 0.0;			//initialize intergral
	
	scale = dp[0];		//make local copies in case memory moves
	rcore = dp[1];
	rshell = dp[2];
	length = dp[3];
	delrho = dp[4];
	bkg = dp[5];
	
	for(i=0;i<nord;i++) {
		zi = ( Gauss76Z[i]*(vb-va) + va + vb )/2.0;
		summ += Gauss76Wt[i] * HolCylKernel(q, rcore, rshell, length, zi);
	}
 	
	answer = (vb-va)/2.0*summ;
	// Multiply by contrast^2
	answer *= delrho*delrho;
	//normalize by volume
	answer *= pi*(rshell*rshell-rcore*rcore)*length;
	//convert to [cm-1]
	answer *= 1.0e8;
	//Scale
	answer *= scale;
	// add in the background
	answer += bkg;
	
	return answer;
}

/*	EllipsoidFormX  :  calculates the form factor of an ellipsoid of revolution with semiaxes a:a:nua
at the given x-value p->x

Uses 76 pt Gaussian quadrature for the single integral

Warning:
The call to WaveData() below returns a pointer to the middle
of an unlocked Macintosh handle. In the unlikely event that your
calculations could cause memory to move, you should copy the coefficient
values to local variables or an array before such operations.
*/
double
EllipsoidForm(double dp[], double q)
{
	int i;
	double scale,a,nua,delrho,bkg;		//local variables of coefficient wave
	int nord=76;			//order of integration
	double va,vb,zi;		//upper and lower integration limits
	double summ,answer,pi;			//running tally of integration
	
	pi = 4.0*atan(1.0);
	va = 0;
	vb = 1;		//limits of numerical integral
	
	summ = 0.0;			//initialize intergral
	
	scale = dp[0];			//make local copies in case memory moves
	nua = dp[1];
	a = dp[2];
	delrho = dp[3];
	bkg = dp[4];
	
	for(i=0;i<nord;i++) {
		zi = ( Gauss76Z[i]*(vb-va) + va + vb )/2.0;
		summ += Gauss76Wt[i] * EllipsoidKernel(q, a, nua, zi);
	}
	
	answer = (vb-va)/2.0*summ;
	// Multiply by contrast^2
	answer *= delrho*delrho;
	//normalize by volume
	answer *= 4*pi/3*a*a*nua;
	//convert to [cm-1]
	answer *= 1.0e8;
	//Scale
	answer *= scale;
	// add in the background
	answer += bkg;
	
	return answer;
}


/*	Cyl_PolyRadiusX  :  calculates the form factor of a cylinder at the given x-value p->x
the cylinder has a polydisperse cross section

*/
double
Cyl_PolyRadius(double dp[], double q)
{
	int i;
	double scale,radius,length,pd,delrho,bkg;		//local variables of coefficient wave
	int nord=20;			//order of integration
	double uplim,lolim;		//upper and lower integration limits
	double summ,zi,yyy,answer,Vpoly;			//running tally of integration
	double range,zz,Pi;
	
	Pi = 4.0*atan(1.0);
	range = 3.4;
	
	summ = 0.0;			//initialize intergral
	
	scale = dp[0];			//make local copies in case memory moves
	radius = dp[1];
	length = dp[2];
	pd = dp[3];
	delrho = dp[4];
	bkg = dp[5];
	
	zz = (1.0/pd)*(1.0/pd) - 1.0;
	
	lolim = radius*(1.0-range*pd);		//set the upper/lower limits to cover the distribution
	if(lolim<0) {
		lolim = 0;
	}
	if(pd>0.3) {
		range = 3.4 + (pd-0.3)*18.0;
	}
	uplim = radius*(1.0+range*pd);
	
	for(i=0;i<nord;i++) {
		zi = ( Gauss20Z[i]*(uplim-lolim) + uplim + lolim )/2.0;
		yyy = Gauss20Wt[i] * Cyl_PolyRadKernel(q, radius, length, zz, delrho, zi);
		summ += yyy;
	}
	
	answer = (uplim-lolim)/2.0*summ;
	//normalize by average cylinder volume
	//NOTE that for this (Fournet) definition of the integral, one must MULTIPLY by Vcyl
	Vpoly=Pi*radius*radius*length*(zz+2.0)/(zz+1.0);
	answer /= Vpoly;
	//convert to [cm-1]
	answer *= 1.0e8;
	//Scale
	answer *= scale;
	// add in the background
	answer += bkg;
	
	return answer;
}

/*	Cyl_PolyLengthX  :  calculates the form factor of a cylinder at the given x-value p->x
the cylinder has a polydisperse Length

*/
double
Cyl_PolyLength(double dp[], double q)
{
	int i;
	double scale,radius,length,pd,delrho,bkg;		//local variables of coefficient wave
	int nord=20;			//order of integration
	double uplim,lolim;		//upper and lower integration limits
	double summ,zi,yyy,answer,Vpoly;			//running tally of integration
	double range,zz,Pi;
	
	
	Pi = 4.0*atan(1.0);
	range = 3.4;
	
	summ = 0.0;			//initialize intergral
	
	scale = dp[0];			//make local copies in case memory moves
	radius = dp[1];
	length = dp[2];
	pd = dp[3];
	delrho = dp[4];
	bkg = dp[5];
	
	zz = (1.0/pd)*(1.0/pd) - 1.0;
	
	lolim = length*(1.0-range*pd);		//set the upper/lower limits to cover the distribution
	if(lolim<0) {
		lolim = 0;
	}
	if(pd>0.3) {
		range = 3.4 + (pd-0.3)*18.0;
	}
	uplim = length*(1.0+range*pd);
	
	for(i=0;i<nord;i++) {
		zi = ( Gauss20Z[i]*(uplim-lolim) + uplim + lolim )/2.0;
		yyy = Gauss20Wt[i] * Cyl_PolyLenKernel(q, radius, length, zz, delrho, zi);
		summ += yyy;
	}
	
	answer = (uplim-lolim)/2.0*summ;
	//normalize by average cylinder volume (first moment)
	//NOTE that for this (Fournet) definition of the integral, one must MULTIPLY by Vcyl
	Vpoly=Pi*radius*radius*length;
	answer /= Vpoly;
	//convert to [cm-1]
	answer *= 1.0e8;
	//Scale
	answer *= scale;
	// add in the background
	answer += bkg;
	
	return answer;
}

/*	CoreShellCylinderX  :  calculates the form factor of a cylinder at the given x-value p->x
the cylinder has a core-shell structure

*/
double
CoreShellCylinder(double dp[], double q)
{
	int i;
	double scale,rcore,length,bkg;		//local variables of coefficient wave
	double thick,rhoc,rhos,rhosolv;
	int nord=76;			//order of integration
	double uplim,lolim,halfheight;		//upper and lower integration limits
	double summ,zi,yyy,answer,Vcyl;			//running tally of integration
	double Pi;
	
	Pi = 4.0*atan(1.0);
	
	lolim = 0.0;
	uplim = Pi/2.0;
	
	summ = 0.0;			//initialize intergral
	
	scale = dp[0];		//make local copies in case memory moves
	rcore = dp[1];
	thick = dp[2];
	length = dp[3];
	rhoc = dp[4];
	rhos = dp[5];
	rhosolv = dp[6];
	bkg = dp[7];
	
	halfheight = length/2.0;
	
	for(i=0;i<nord;i++) {
		zi = ( Gauss76Z[i]*(uplim-lolim) + uplim + lolim )/2.0;
		yyy = Gauss76Wt[i] * CoreShellCylKernel(q, rcore, thick, rhoc,rhos,rhosolv, halfheight, zi);
		summ += yyy;
	}
	
	answer = (uplim-lolim)/2.0*summ;
	// length is the total core length 
	Vcyl=Pi*(rcore+thick)*(rcore+thick)*(length+2.0*thick);
	answer /= Vcyl;
	//convert to [cm-1]
	answer *= 1.0e8;
	//Scale
	answer *= scale;
	// add in the background
	answer += bkg;
	
	return answer;
}


/*	PolyCoShCylinderX  :  calculates the form factor of a core-shell cylinder at the given x-value p->x
the cylinder has a polydisperse CORE radius

*/
double
PolyCoShCylinder(double dp[], double q)
{
	int i;
	double scale,radius,length,sigma,bkg;		//local variables of coefficient wave
	double rad,radthick,facthick,rhoc,rhos,rhosolv;
	int nord=20;			//order of integration
	double uplim,lolim;		//upper and lower integration limits
	double summ,yyy,answer,Vpoly;			//running tally of integration
	double Pi,AR,Rsqrsumm,Rsqryyy,Rsqr;
	
	Pi = 4.0*atan(1.0);
	
	summ = 0.0;			//initialize intergral
	Rsqrsumm = 0.0;
	
	scale = dp[0];
	radius = dp[1];
	sigma = dp[2];				//sigma is the standard mean deviation
	length = dp[3];
	radthick = dp[4];
	facthick= dp[5];
	rhoc = dp[6];
	rhos = dp[7];
	rhosolv = dp[8];
	bkg = dp[9];
	
	lolim = exp(log(radius)-(4.*sigma));
	if (lolim<0) {
		lolim=0;		//to avoid numerical error when  va<0 (-ve r value)
	}
	uplim = exp(log(radius)+(4.*sigma));
	
	for(i=0;i<nord;i++) {
		rad = ( Gauss20Z[i]*(uplim-lolim) + uplim + lolim )/2.0;
		AR=(1.0/(rad*sigma*sqrt(2.0*Pi)))*exp(-(0.5*((log(radius/rad))/sigma)*((log(radius/rad))/sigma)));
		yyy = AR* Gauss20Wt[i] * CSCylIntegration(q,rad,radthick,facthick,rhoc,rhos,rhosolv,length);
		Rsqryyy= Gauss20Wt[i] * AR * (rad+radthick)*(rad+radthick);		//SRK normalize to total dimensions
		summ += yyy;
		Rsqrsumm += Rsqryyy;
	}
	
	answer = (uplim-lolim)/2.0*summ;
	Rsqr = (uplim-lolim)/2.0*Rsqrsumm;
	//normalize by average cylinder volume
	Vpoly = Pi*Rsqr*(length+2*facthick);
	answer /= Vpoly;
	//convert to [cm-1]
	answer *= 1.0e8;
	//Scale
	answer *= scale;
	// add in the background
	answer += bkg;
	
	return answer;
}

/*	OblateFormX  :  calculates the form factor of a core-shell Oblate ellipsoid at the given x-value p->x
the ellipsoid has a core-shell structure

*/
double
OblateForm(double dp[], double q)
{
	int i;
	double scale,crmaj,crmin,trmaj,trmin,delpc,delps,bkg;
	int nord=76;			//order of integration
	double uplim,lolim;		//upper and lower integration limits
	double summ,zi,yyy,answer,oblatevol;			//running tally of integration
	double Pi;
	
	Pi = 4.0*atan(1.0);
	
	lolim = 0.0;
	uplim = 1.0;
	
	summ = 0.0;			//initialize intergral
	
	
	scale = dp[0];		//make local copies in case memory moves
	crmaj = dp[1];
	crmin = dp[2];
	trmaj = dp[3];
	trmin = dp[4];
	delpc = dp[5];
	delps = dp[6];
	bkg = dp[7];                        
	
	for(i=0;i<nord;i++) {
		zi = ( Gauss76Z[i]*(uplim-lolim) + uplim + lolim )/2.0;
		yyy = Gauss76Wt[i] * gfn4(zi,crmaj,crmin,trmaj,trmin,delpc,delps,q);
		summ += yyy;
	}
	
	answer = (uplim-lolim)/2.0*summ;
	// normalize by particle volume
	oblatevol = 4*Pi/3*trmaj*trmaj*trmin;
	answer /= oblatevol;
	
	//convert to [cm-1]
	answer *= 1.0e8;
	//Scale
	answer *= scale;
	// add in the background
	answer += bkg;
	
	return answer;
}

/*	ProlateFormX  :  calculates the form factor of a core-shell Prolate ellipsoid at the given x-value p->x
the ellipsoid has a core-shell structure

*/
double
ProlateForm(double dp[], double q)
{
	int i;
	double scale,crmaj,crmin,trmaj,trmin,delpc,delps,bkg;
	int nord=76;			//order of integration
	double uplim,lolim;		//upper and lower integration limits
	double summ,zi,yyy,answer,prolatevol;			//running tally of integration
	double Pi;
	
	Pi = 4.0*atan(1.0);
	
	lolim = 0.0;
	uplim = 1.0;
	
	summ = 0.0;			//initialize intergral
	
	scale = dp[0];		//make local copies in case memory moves
	crmaj = dp[1];
	crmin = dp[2];
	trmaj = dp[3];
	trmin = dp[4];
	delpc = dp[5];
	delps = dp[6];
	bkg = dp[7];                        
	
	for(i=0;i<nord;i++) {
		zi = ( Gauss76Z[i]*(uplim-lolim) + uplim + lolim )/2.0;
		yyy = Gauss76Wt[i] * gfn2(zi,crmaj,crmin,trmaj,trmin,delpc,delps,q);
		summ += yyy;
	}
	
	answer = (uplim-lolim)/2.0*summ;
	// normalize by particle volume
	prolatevol = 4*Pi/3*trmaj*trmin*trmin;
	answer /= prolatevol;
	
	//convert to [cm-1]
	answer *= 1.0e8;
	//Scale
	answer *= scale;
	// add in the background
	answer += bkg;
	
	return answer;
}


/*	StackedDiscsX  :  calculates the form factor of a stacked "tactoid" of core shell disks
like clay platelets that are not exfoliated

*/
double
StackedDiscs(double dp[], double q)
{
	int i;
	double scale,length,bkg,rcore,thick,rhoc,rhol,rhosolv,N,gsd;		//local variables of coefficient wave
	double va,vb,vcyl,summ,yyy,zi,halfheight,d,answer;
	int nord=76;			//order of integration
	double Pi;
	
	
	Pi = 4.0*atan(1.0);
	
	va = 0.0;
	vb = Pi/2.0;
	
	summ = 0.0;			//initialize intergral
	
	scale = dp[0];
	rcore = dp[1];
	length = dp[2];
	thick = dp[3];
	rhoc = dp[4];
	rhol = dp[5];
	rhosolv = dp[6];
	N = dp[7];
	gsd = dp[8];
	bkg = dp[9];
	
	d=2.0*thick+length;
	halfheight = length/2.0;
	
	for(i=0;i<nord;i++) {
		zi = ( Gauss76Z[i]*(vb-va) + vb + va )/2.0;
		yyy = Gauss76Wt[i] * Stackdisc_kern(q, rcore, rhoc,rhol,rhosolv, halfheight,thick,zi,gsd,d,N);
		summ += yyy;
	}
	
	answer = (vb-va)/2.0*summ;
	// length is the total core length 
	vcyl=Pi*rcore*rcore*(2.0*thick+length)*N;
	answer /= vcyl;
	//Convert to [cm-1]
	answer *= 1.0e8;
	//Scale
	answer *= scale;
	// add in the background
	answer += bkg;
	
	return answer;
}


/*	LamellarFFX  :  calculates the form factor of a lamellar structure - no S(q) effects included

*/
double
LamellarFF(double dp[], double q)
{
	double scale,del,sig,contr,bkg;		//local variables of coefficient wave
	double inten, qval,Pq;
	double Pi;
	
	
	Pi = 4.0*atan(1.0);
	scale = dp[0];
	del = dp[1];
	sig = dp[2]*del;
	contr = dp[3];
	bkg = dp[4];
	qval = q;
	
	Pq = 2.0*contr*contr/qval/qval*(1.0-cos(qval*del)*exp(-0.5*qval*qval*sig*sig));
	
	inten = 2.0*Pi*scale*Pq/(qval*qval);		//this is now dimensionless...
	
	inten /= del;			//normalize by the thickness (in A)
	
	inten *= 1.0e8;		// 1/A to 1/cm
	
	return(inten+bkg);
}

/*	LamellarPSX  :  calculates the form factor of a lamellar structure - with S(q) effects included
-------
------- resolution effects ARE included, but only a CONSTANT default value, not the real q-dependent resolution!!

	*/
double
LamellarPS(double dp[], double q)
{
	double scale,dd,del,sig,contr,NN,Cp,bkg;		//local variables of coefficient wave
	double inten, qval,Pq,Sq,alpha,temp,t1,t2,t3,dQ;
	double Pi,Euler,dQDefault,fii;
	int ii,NNint;
	
	Euler = 0.5772156649;		// Euler's constant
	dQDefault = 0.0025;		//[=] 1/A, q-resolution, default value
	dQ = dQDefault;
	
	Pi = 4.0*atan(1.0);
	qval = q;
	
	scale = dp[0];
	dd = dp[1];
	del = dp[2];
	sig = dp[3]*del;
	contr = dp[4];
	NN = trunc(dp[5]);		//be sure that NN is an integer
	Cp = dp[6];
	bkg = dp[7];
	
	Pq = 2.0*contr*contr/qval/qval*(1.0-cos(qval*del)*exp(-0.5*qval*qval*sig*sig));
	
	NNint = (int)NN;		//cast to an integer for the loop
	ii=0;
	Sq = 0.0;
	for(ii=1;ii<(NNint-1);ii+=1) {
        
		fii = (double)ii;		//do I really need to do this?
		
		temp = 0.0;
		alpha = Cp/4.0/Pi/Pi*(log(Pi*ii) + Euler);
		t1 = 2.0*dQ*dQ*dd*dd*alpha;
		t2 = 2.0*qval*qval*dd*dd*alpha;
		t3 = dQ*dQ*dd*dd*ii*ii;
		
		temp = 1.0-ii/NN;
		temp *= cos(dd*qval*ii/(1.0+t1));
		temp *= exp(-1.0*(t2 + t3)/(2.0*(1.0+t1)) );
		temp /= sqrt(1.0+t1);
		
		Sq += temp;
	}
	
	Sq *= 2.0;
	Sq += 1.0;
	
	inten = 2.0*Pi*scale*Pq*Sq/(dd*qval*qval);
	
	inten *= 1.0e8;		// 1/A to 1/cm
	
    return(inten+bkg);
}


/*	LamellarPS_HGX  :  calculates the form factor of a lamellar structure - with S(q) effects included
-------
------- resolution effects ARE included, but only a CONSTANT default value, not the real q-dependent resolution!!

	*/
double
LamellarPS_HG(double dp[], double q)
{
	double scale,dd,delT,delH,SLD_T,SLD_H,SLD_S,NN,Cp,bkg;		//local variables of coefficient wave
	double inten,qval,Pq,Sq,alpha,temp,t1,t2,t3,dQ,drh,drt;
	double Pi,Euler,dQDefault,fii;
	int ii,NNint;
	
	
	Euler = 0.5772156649;		// Euler's constant
	dQDefault = 0.0025;		//[=] 1/A, q-resolution, default value
	dQ = dQDefault;
	
	Pi = 4.0*atan(1.0);
	qval= q;
	
	scale = dp[0];
	dd = dp[1];
	delT = dp[2];
	delH = dp[3];
	SLD_T = dp[4];
	SLD_H = dp[5];
	SLD_S = dp[6];
	NN = trunc(dp[7]);		//be sure that NN is an integer
	Cp = dp[8];
	bkg = dp[9];
	
	
	drh = SLD_H - SLD_S;
	drt = SLD_T - SLD_S;	//correction 13FEB06 by L.Porcar
	
	Pq = drh*(sin(qval*(delH+delT))-sin(qval*delT)) + drt*sin(qval*delT);
	Pq *= Pq;
	Pq *= 4.0/(qval*qval);
	
	NNint = (int)NN;		//cast to an integer for the loop
	ii=0;
	Sq = 0.0;
	for(ii=1;ii<(NNint-1);ii+=1) {
        
		fii = (double)ii;		//do I really need to do this?
		
		temp = 0.0;
		alpha = Cp/4.0/Pi/Pi*(log(Pi*ii) + Euler);
		t1 = 2.0*dQ*dQ*dd*dd*alpha;
		t2 = 2.0*qval*qval*dd*dd*alpha;
		t3 = dQ*dQ*dd*dd*ii*ii;
		
		temp = 1.0-ii/NN;
		temp *= cos(dd*qval*ii/(1.0+t1));
		temp *= exp(-1.0*(t2 + t3)/(2.0*(1.0+t1)) );
		temp /= sqrt(1.0+t1);
		
		Sq += temp;
	}
	
	Sq *= 2.0;
	Sq += 1.0;
	
	inten = 2.0*Pi*scale*Pq*Sq/(dd*qval*qval);
	
	inten *= 1.0e8;		// 1/A to 1/cm
	
	return(inten+bkg);
}

/*	LamellarFF_HGX  :  calculates the form factor of a lamellar structure - no S(q) effects included
but extra SLD for head groups is included

*/
double
LamellarFF_HG(double dp[], double q)
{
	double scale,delT,delH,slds,sldh,sldt,bkg;		//local variables of coefficient wave
	double inten, qval,Pq,drh,drt;
	double Pi;
	
	
	Pi = 4.0*atan(1.0);
	qval= q;
	scale = dp[0];
	delT = dp[1];
	delH = dp[2];
	sldt = dp[3];
	sldh = dp[4];
	slds = dp[5];
	bkg = dp[6];
	
	
	drh = sldh - slds;
	drt = sldt - slds;		//correction 13FEB06 by L.Porcar
	
	Pq = drh*(sin(qval*(delH+delT))-sin(qval*delT)) + drt*sin(qval*delT);
	Pq *= Pq;
	Pq *= 4.0/(qval*qval);
	
	inten = 2.0*Pi*scale*Pq/(qval*qval);		//dimensionless...
	
	inten /= 2.0*(delT+delH);			//normalize by the bilayer thickness
	
	inten *= 1.0e8;		// 1/A to 1/cm
	
	return(inten+bkg);
}

/*	FlexExclVolCylX  :  calculates the form factor of a flexible cylinder with a circular cross section
-- incorporates Wei-Ren Chen's fixes - 2006

	*/
double
FlexExclVolCyl(double dp[], double q)
{
	double scale,L,B,bkg,rad,qr,cont;
	double Pi,flex,crossSect,answer;
	
	
	Pi = 4.0*atan(1.0);
	
	scale = dp[0];		//make local copies in case memory moves
	L = dp[1];
	B = dp[2];
	rad = dp[3];
	cont = dp[4];
	bkg = dp[5];
	
    
	qr = q*rad;
	
	flex = Sk_WR(q,L,B);
	
	crossSect = (2.0*NR_BessJ1(qr)/qr)*(2.0*NR_BessJ1(qr)/qr);
	flex *= crossSect;
	flex *= Pi*rad*rad*L;
	flex *= cont*cont;
	flex *= 1.0e8;
	answer = scale*flex + bkg;
	
	return answer;
}

/*	FlexCyl_EllipX  :  calculates the form factor of a flexible cylinder with an elliptical cross section
-- incorporates Wei-Ren Chen's fixes - 2006

	*/
double
FlexCyl_Ellip(double dp[], double q)
{
	double scale,L,B,bkg,rad,qr,cont,ellRatio;
	double Pi,flex,crossSect,answer;
	
	
	Pi = 4.0*atan(1.0);
	scale = dp[0];		//make local copies in case memory moves
	L = dp[1];
	B = dp[2];
	rad = dp[3];
	ellRatio = dp[4];
	cont = dp[5];
	bkg = dp[6];
	
	qr = q*rad;
	
	flex = Sk_WR(q,L,B);
	
	crossSect = EllipticalCross_fn(q,rad,(rad*ellRatio));
	flex *= crossSect;
	flex *= Pi*rad*rad*ellRatio*L;
	flex *= cont*cont;
	flex *= 1.0e8;
	answer = scale*flex + bkg;
	
	return answer;
}

double
EllipticalCross_fn(double qq, double a, double b)
{
    double uplim,lolim,Pi,summ,arg,zi,yyy,answer;
    int i,nord=76;
    
    Pi = 4.0*atan(1.0);
    lolim=0.0;
    uplim=Pi/2.0;
    summ=0.0;
    
    for(i=0;i<nord;i++) {
		zi = ( Gauss76Z[i]*(uplim-lolim) + uplim + lolim )/2.0;
		arg = qq*sqrt(a*a*sin(zi)*sin(zi)+b*b*cos(zi)*cos(zi));
		yyy = pow((2.0 * NR_BessJ1(arg) / arg),2);
		yyy *= Gauss76Wt[i];
		summ += yyy;
    }
    answer = (uplim-lolim)/2.0*summ;
    answer *= 2.0/Pi;
    return(answer);
	
}
/*	FlexCyl_PolyLenX  :  calculates the form factor of a flecible cylinder at the given x-value p->x
the cylinder has a polydisperse Length

*/
double
FlexCyl_PolyLen(double dp[], double q)
{
	int i;
	double scale,radius,length,pd,delrho,bkg,lb;		//local variables of coefficient wave
	int nord=20;			//order of integration
	double uplim,lolim;		//upper and lower integration limits
	double summ,zi,yyy,answer,Vpoly;			//running tally of integration
	double range,zz,Pi;
	
	Pi = 4.0*atan(1.0);
	range = 3.4;
	
	summ = 0.0;			//initialize intergral
	scale = dp[0];			//make local copies in case memory moves
	length = dp[1];			//radius
	pd = dp[2];			// average length
	lb = dp[3];
	radius = dp[4];
	delrho = dp[5];
	bkg = dp[6];
	
	zz = (1.0/pd)*(1.0/pd) - 1.0;
	
	lolim = length*(1.0-range*pd);		//set the upper/lower limits to cover the distribution
	if(lolim<0) {
		lolim = 0;
	}
	if(pd>0.3) {
		range = 3.4 + (pd-0.3)*18.0;
	}
	uplim = length*(1.0+range*pd);
	
	for(i=0;i<nord;i++) {
		zi = ( Gauss20Z[i]*(uplim-lolim) + uplim + lolim )/2.0;
		yyy = Gauss20Wt[i] * FlePolyLen_kernel(q,radius,length,lb,zz,delrho,zi);
		summ += yyy;
	}
	
	answer = (uplim-lolim)/2.0*summ;
	//normalize by average cylinder volume (first moment), using the average length
	Vpoly=Pi*radius*radius*length;
	answer /= Vpoly;
	
	answer *=delrho*delrho;
	
	//convert to [cm-1]
	answer *= 1.0e8;
	//Scale
	answer *= scale;
	// add in the background
	answer += bkg;
	
	return answer;
}

/*	FlexCyl_PolyLenX  :  calculates the form factor of a flexible cylinder at the given x-value p->x
the cylinder has a polydisperse cross sectional radius

*/
double
FlexCyl_PolyRad(double dp[], double q)
{
	int i;
	double scale,radius,length,pd,delrho,bkg,lb;		//local variables of coefficient wave
	int nord=76;			//order of integration
	double uplim,lolim;		//upper and lower integration limits
	double summ,zi,yyy,answer,Vpoly;			//running tally of integration
	double range,zz,Pi;
	
	
	Pi = 4.0*atan(1.0);
	range = 3.4;
	
	summ = 0.0;			//initialize intergral
	
	scale = dp[0];			//make local copies in case memory moves
	length = dp[1];			//radius
	lb = dp[2];			// average length
	radius = dp[3];
	pd = dp[4];
	delrho = dp[5];
	bkg = dp[6];
	
	zz = (1.0/pd)*(1.0/pd) - 1.0;
	
	lolim = radius*(1.0-range*pd);		//set the upper/lower limits to cover the distribution
	if(lolim<0) {
		lolim = 0;
	}
	if(pd>0.3) {
		range = 3.4 + (pd-0.3)*18.0;
	}
	uplim = radius*(1.0+range*pd);
	
	for(i=0;i<nord;i++) {
		//zi = ( Gauss20Z[i]*(uplim-lolim) + uplim + lolim )/2.0;
		//yyy = Gauss20Wt[i] * FlePolyRad_kernel(q,radius,length,lb,zz,delrho,zi);
		zi = ( Gauss76Z[i]*(uplim-lolim) + uplim + lolim )/2.0;
		yyy = Gauss76Wt[i] * FlePolyRad_kernel(q,radius,length,lb,zz,delrho,zi);
		summ += yyy;
	}
	
	answer = (uplim-lolim)/2.0*summ;
	//normalize by average cylinder volume (second moment), using the average radius
	Vpoly = Pi*radius*radius*length*(zz+2.0)/(zz+1.0);
	answer /= Vpoly;
	
	answer *=delrho*delrho;
	
	//convert to [cm-1]
	answer *= 1.0e8;
	//Scale
	answer *= scale;
	// add in the background
	answer += bkg;
	
	return answer;
}

/////////functions for WRC implementation of flexible cylinders
static double
Sk_WR(double q, double L, double b)
{
	//
	double p1,p2,p1short,p2short,q0,qconnect;
	double C,epsilon,ans,q0short,Sexvmodify,pi;
	
	pi = 4.0*atan(1.0);
	
	p1 = 4.12;
	p2 = 4.42;
	p1short = 5.36;
	p2short = 5.62;
	q0 = 3.1;
	qconnect = q0/b;
	//	
	q0short = fmax(1.9/sqrt(Rgsquareshort(q,L,b)),3.0);
	
	//
	if(L/b > 10.0) {
		C = 3.06/pow((L/b),0.44);
		epsilon = 0.176;
	} else {
		C = 1.0;
		epsilon = 0.170;
	}
	//
	
	if( L > 4*b ) { // Longer Chains
		if (q*b <= 3.1) {		//Modified by Yun on Oct. 15,
			Sexvmodify = Sexvnew(q, L, b);
			ans = Sexvmodify + C * (4.0/15.0 + 7.0/(15.0*u_WR(q,L,b)) - (11.0/15.0 + 7.0/(15.0*u_WR(q,L,b)))*exp(-u_WR(q,L,b)))*(b/L);
		} else { //q(i)*b > 3.1
			ans = a1long(q, L, b, p1, p2, q0)/(pow((q*b),p1)) + a2long(q, L, b, p1, p2, q0)/(pow((q*b),p2)) + pi/(q*L);
		} 
	} else { //L <= 4*b Shorter Chains
		if (q*b <= fmax(1.9/sqrt(Rgsquareshort(q,L,b)),3.0) ) {
			if (q*b<=0.01) {
				ans = 1.0 - Rgsquareshort(q,L,b)*(q*q)/3.0;
			} else {
				ans = Sdebye1(q,L,b);
			}
		} else {	//q*b > max(1.9/sqrt(Rgsquareshort(q(i),L,b)),3)
			ans = a1short(q,L,b,p1short,p2short,q0short)/(pow((q*b),p1short)) + a2short(q,L,b,p1short,p2short,q0short)/(pow((q*b),p2short)) + pi/(q*L);
		}
	}
	
	return(ans);
	//return(a2long(q, L, b, p1, p2, q0));
}

//WR named this w (too generic)
static double
w_WR(double x)
{
    double yy;
    yy = 0.5*(1 + tanh((x - 1.523)/0.1477));
	
    return (yy);
}

//
static double
u1(double q, double L, double b)
{
    double yy;
	
    yy = Rgsquareshort(q,L,b)*q*q;
    
    return (yy);
}

// was named u
static double
u_WR(double q, double L, double b)
{
    double yy;
    yy = Rgsquare(q,L,b)*q*q;
    return (yy);
}



//
static double
Rgsquarezero(double q, double L, double b)
{    
    double yy;
    yy = (L*b/6.0) * (1.0 - 1.5*(b/L) + 1.5*pow((b/L),2) - 0.75*pow((b/L),3)*(1.0 - exp(-2.0*(L/b))));
    
    return (yy);
}

//
static double
Rgsquareshort(double q, double L, double b)
{    
    double yy;
    yy = AlphaSquare(L/b) * Rgsquarezero(q,L,b);
    
    return (yy);
}

//
static double
Rgsquare(double q, double L, double b)
{
    double yy;
    yy = AlphaSquare(L/b)*L*b/6.0;
    
    return (yy);
}

//
static double
AlphaSquare(double x)
{    
    double yy;
    yy = pow( (1.0 + (x/3.12)*(x/3.12) + (x/8.67)*(x/8.67)*(x/8.67)),(0.176/3.0) );
	
    return (yy);
}

// ?? funciton is not used - but should the log actually be log10???
static double
miu(double x)
{    
    double yy;
    yy = (1.0/8.0)*(9.0*x - 2.0 + 2.0*log(1.0 + x)/x)*exp(1.0/2.565*(1.0/x + (1.0 - 1.0/(x*x))*log(1.0 + x)));
    
    return (yy);
}

//
static double
Sdebye(double q, double L, double b)
{    
    double yy;
    yy = 2.0*(exp(-u_WR(q,L,b)) + u_WR(q,L,b) -1.0)/(pow((u_WR(q,L,b)),2));
	
    return (yy);
}

//
static double
Sdebye1(double q, double L, double b)
{    
    double yy;
    yy = 2.0*(exp(-u1(q,L,b)) + u1(q,L,b) -1.0)/( pow((u1(q,L,b)),2.0) );
    
    return (yy);
}

//
static double
Sexv(double q, double L, double b)
{    
    double yy,C1,C2,C3,miu,Rg2;
    C1=1.22;
    C2=0.4288;
    C3=-1.651;
    miu = 0.585;
	
    Rg2 = Rgsquare(q,L,b);
    
    yy = (1.0 - w_WR(q*sqrt(Rg2)))*Sdebye(q,L,b) + w_WR(q*sqrt(Rg2))*(C1*pow((q*sqrt(Rg2)),(-1.0/miu)) +  C2*pow((q*sqrt(Rg2)),(-2.0/miu)) +    C3*pow((q*sqrt(Rg2)),(-3.0/miu)));
    
    return (yy);
}

// this must be WR modified version
static double
Sexvnew(double q, double L, double b)
{    
    double yy,C1,C2,C3,miu;
    double del=1.05,C_star2,Rg2;
    
    C1=1.22;
    C2=0.4288;
    C3=-1.651;
    miu = 0.585;
	
    //calculating the derivative to decide on the corection (cutoff) term?
    // I have modified this from WRs original code
    
    if( (Sexv(q*del,L,b)-Sexv(q,L,b))/(q*del - q) >= 0.0 ) {
        C_star2 = 0.0;
    } else {
        C_star2 = 1.0;
    }
	
    Rg2 = Rgsquare(q,L,b);
    
	yy = (1.0 - w_WR(q*sqrt(Rg2)))*Sdebye(q,L,b) + C_star2*w_WR(q*sqrt(Rg2))*(C1*pow((q*sqrt(Rg2)),(-1.0/miu)) + C2*pow((q*sqrt(Rg2)),(-2.0/miu)) + C3*pow((q*sqrt(Rg2)),(-3.0/miu)));
	
    return (yy);
}

// these are the messy ones
static double
a2short(double q, double L, double b, double p1short, double p2short, double q0)
{    
    double yy,Rg2_sh;
    double t1,E,Rg2_sh2,Et1,Emt1,q02,q0p;
    double pi;
	
    E = 2.718281828459045091;
	pi = 4.0*atan(1.0);
    Rg2_sh = Rgsquareshort(q,L,b);
    Rg2_sh2 = Rg2_sh*Rg2_sh;
    t1 = ((q0*q0*Rg2_sh)/(b*b));
    Et1 = pow(E,t1);
    Emt1 =pow(E,-t1); 
    q02 = q0*q0;
    q0p = pow(q0,(-4.0 + p2short) );
    
    //E is the number e
    yy = ((-(1.0/(L*((p1short - p2short))*Rg2_sh2)*((b*Emt1*q0p*((8.0*b*b*b*L - 8.0*b*b*b*Et1*L - 2.0*b*b*b*L*p1short + 2.0*b*b*b*Et1*L*p1short + 4.0*b*L*q02*Rg2_sh + 4.0*b*Et1*L*q02*Rg2_sh - 2.0*b*Et1*L*p1short*q02*Rg2_sh - Et1*pi*q02*q0*Rg2_sh2 + Et1*p1short*pi*q02*q0*Rg2_sh2)))))));
	
    return (yy);
}

//
static double
a1short(double q, double L, double b, double p1short, double p2short, double q0)
{    
    double yy,Rg2_sh;
    double t1,E,Rg2_sh2,Et1,Emt1,q02,q0p,b3;
	double pi;
    
    E = 2.718281828459045091;
	pi = 4.0*atan(1.0);
    Rg2_sh = Rgsquareshort(q,L,b);
    Rg2_sh2 = Rg2_sh*Rg2_sh;
    b3 = b*b*b;
    t1 = ((q0*q0*Rg2_sh)/(b*b));
    Et1 = pow(E,t1);
    Emt1 =pow(E,-t1); 
    q02 = q0*q0;
    q0p = pow(q0,(-4.0 + p1short) );
    
    yy = ((1.0/(L*((p1short - p2short))*Rg2_sh2)*((b*Emt1*q0p*((8.0*b3*L - 8.0*b3*Et1*L - 2.0*b3*L*p2short + 2.0*b3*Et1*L*p2short + 4.0*b*L*q02*Rg2_sh + 4.0*b*Et1*L*q02*Rg2_sh - 2.0*b*Et1*L*p2short*q02*Rg2_sh - Et1*pi*q02*q0*Rg2_sh2 + Et1*p2short*pi*q02*q0*Rg2_sh2)))))); 
	
    return(yy);
}

// this one will be lots of trouble
static double
a2long(double q, double L, double b, double p1, double p2, double q0)
{
    double yy,C1,C2,C3,C4,C5,miu,C,Rg2;
    double t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,pi;
    double E,b2,b3,b4,q02,q03,q04,q05,Rg22;
    
    pi = 4.0*atan(1.0);
    E = 2.718281828459045091;
    if( L/b > 10.0) {
        C = 3.06/pow((L/b),0.44);
    } else {
        C = 1.0;
    }
	
    C1 = 1.22;
    C2 = 0.4288;
    C3 = -1.651;
    C4 = 1.523;
    C5 = 0.1477;
    miu = 0.585;
	
    Rg2 = Rgsquare(q,L,b);
    Rg22 = Rg2*Rg2;
    b2 = b*b;
    b3 = b*b*b;
    b4 = b3*b;
    q02 = q0*q0;
    q03 = q0*q0*q0;
    q04 = q03*q0;
    q05 = q04*q0;
    
    t1 = (1.0/(b* p1*pow(q0,((-1.0) - p1 - p2)) - b*p2*pow(q0,((-1.0) - p1 - p2)) ));
    
    t2 = (b*C*(((-1.0*((14.0*b3)/(15.0*q03*Rg2))) + (14*b3*pow(E,(-((q02*Rg2)/b2))))/(15*q03*Rg2) + (2*pow(E,(-((q02*Rg2)/b2)))*q0*((11.0/15.0 + (7*b2)/(15*q02*Rg2)))*Rg2)/b)))/L;
    
    t3 = (sqrt(Rg2)*((C3*pow((((sqrt(Rg2)*q0)/b)),((-3)/miu)) + C2*pow((((sqrt(Rg2)*q0)/b)),((-2)/miu)) + C1*pow((((sqrt(Rg2)*q0)/b)),((-1.0)/miu))))*pow(sech_WR(((-C4) + (sqrt(Rg2)*q0)/b)/C5),2))/(2*C5);
    
    t4 = (b4*sqrt(Rg2)*(((-1) + pow(E,(-((q02*Rg2)/b2))) + (q02*Rg2)/b2))*pow(sech_WR(((-C4) + (sqrt(Rg2)*q0)/b)/C5),2))/(C5*q04*Rg22);
    
    t5 = (2*b4*(((2*q0*Rg2)/b - (2*pow(E,(-((q02*Rg2)/b2)))*q0*Rg2)/b))*((1 + 1.0/2.0*(((-1) - tanh(((-C4) + (sqrt(Rg2)*q0)/b)/C5))))))/(q04*Rg22);
    
    t6 = (8*b4*b*(((-1) + pow(E,(-((q02*Rg2)/b2))) + (q02*Rg2)/b2))*((1 + 1.0/2.0*(((-1) - tanh(((-C4) + (sqrt(Rg2)*q0)/b)/C5))))))/(q05*Rg22);
    
    t7 = (((-((3*C3*sqrt(Rg2)*pow((((sqrt(Rg2)*q0)/b)),((-1) - 3/miu)))/miu)) - (2*C2*sqrt(Rg2)*pow((((sqrt(Rg2)*q0)/b)),((-1) - 2/miu)))/miu - (C1*sqrt(Rg2)*pow((((sqrt(Rg2)*q0)/b)),((-1) - 1/miu)))/miu));
    
    t8 = ((1 + tanh(((-C4) + (sqrt(Rg2)*q0)/b)/C5)));
    
    t9 = (b*C*((4.0/15.0 - pow(E,(-((q02*Rg2)/b2)))*((11.0/15.0 + (7*b2)/(15*q02*Rg2))) + (7*b2)/(15*q02*Rg2))))/L;
    
    t10 = (2*b4*(((-1) + pow(E,(-((q02*Rg2)/b2))) + (q02*Rg2)/b2))*((1 + 1.0/2.0*(((-1) - tanh(((-C4) + (sqrt(Rg2)*q0)/b)/C5))))))/(q04*Rg22);
	
    
    yy = ((-1*(t1* ((-pow(q0,-p1)*(((b2*pi)/(L*q02) + t2 + t3 - t4 + t5 - t6 + 1.0/2.0*t7*t8)) - b*p1*pow(q0,((-1) - p1))*(((-((b*pi)/(L*q0))) + t9 + t10 + 1.0/2.0*((C3*pow((((sqrt(Rg2)*q0)/b)),((-3)/miu)) + C2*pow((((sqrt(Rg2)*q0)/b)),((-2)/miu)) + C1*pow((((sqrt(Rg2)*q0)/b)),((-1)/miu))))*((1 + tanh(((-C4) + (sqrt(Rg2)*q0)/b)/C5))))))))));
	
    return (yy);
}

//need to define this on my own
static double
sech_WR(double x)
{	
	return(1/cosh(x));
}

//
static double
a1long(double q, double L, double b, double p1, double p2, double q0)
{    
    double yy,C,C1,C2,C3,C4,C5,miu,Rg2;
    double t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,t13,t14,t15;
    double E,pi;
    double b2,b3,b4,q02,q03,q04,q05,Rg22;
	
    pi = 4.0*atan(1.0);
    E = 2.718281828459045091;
    
    if( L/b > 10.0) {
        C = 3.06/pow((L/b),0.44);
    } else {
        C = 1.0;
    }
	
    C1 = 1.22;
    C2 = 0.4288;
    C3 = -1.651;
    C4 = 1.523;
    C5 = 0.1477;
    miu = 0.585;
	
    Rg2 = Rgsquare(q,L,b);
    Rg22 = Rg2*Rg2;
    b2 = b*b;
    b3 = b*b*b;
    b4 = b3*b;
    q02 = q0*q0;
    q03 = q0*q0*q0;
    q04 = q03*q0;
    q05 = q04*q0;
    
    t1 = (b*C*((4.0/15.0 - pow(E,(-((q02*Rg2)/b2)))*((11.0/15.0 + (7.0*b2)/(15.0*q02*Rg2))) + (7.0*b2)/(15.0*q02*Rg2))));
    
    t2 = (2.0*b4*(((-1.0) + pow(E,(-((q02*Rg2)/b2))) + (q02*Rg2)/b2))*((1.0 + 1.0/2.0*(((-1.0) - tanh(((-C4) + (sqrt(Rg2)*q0)/b)/C5))))));
    
    t3 = ((C3*pow((((sqrt(Rg2)*q0)/b)),((-3.0)/miu)) + C2*pow((((sqrt(Rg2)*q0)/b)),((-2.0)/miu)) + C1*pow((((sqrt(Rg2)*q0)/b)),((-1.0)/miu))));
    
    t4 = ((1.0 + tanh(((-C4) + (sqrt(Rg2)*q0)/b)/C5)));
	
    t5 = (1.0/(b*p1*pow(q0,((-1.0) - p1 - p2)) - b*p2*pow(q0,((-1.0) - p1 - p2))));
    
    t6 = (b*C*(((-((14.0*b3)/(15.0*q03*Rg2))) + (14.0*b3*pow(E,(-((q02*Rg2)/b2))))/(15.0*q03*Rg2) + (2.0*pow(E,(-((q02*Rg2)/b2)))*q0*((11.0/15.0 + (7.0*b2)/(15.0*q02*Rg2)))*Rg2)/b)));
    
    t7 = (sqrt(Rg2)*((C3*pow((((sqrt(Rg2)*q0)/b)),((-3.0)/miu)) + C2*pow((((sqrt(Rg2)*q0)/b)),((-2.0)/miu)) + C1*pow((((sqrt(Rg2)*q0)/b)),((-1.0)/miu))))*pow(sech_WR(((-C4) + (sqrt(Rg2)*q0)/b)/C5),2));
    
    t8 = (b4*sqrt(Rg2)*(((-1.0) + pow(E,(-((q02*Rg2)/b2))) + (q02*Rg2)/b2))*pow(sech_WR(((-C4) + (sqrt(Rg2)*q0)/b)/C5),2));
    
    t9 = (2.0*b4*(((2.0*q0*Rg2)/b - (2.0*pow(E,(-((q02*Rg2)/b2)))*q0*Rg2)/b))*((1.0 + 1.0/2.0*(((-1.0) - tanh(((-C4) + (sqrt(Rg2)*q0)/b)/C5))))));
    
    t10 = (8.0*b4*b*(((-1.0) + pow(E,(-((q02*Rg2)/b2))) + (q02*Rg2)/b2))*((1.0 + 1.0/2.0*(((-1.0) - tanh(((-C4) + (sqrt(Rg2)*q0)/b)/C5))))));
    
    t11 = (((-((3.0*C3*sqrt(Rg2)*pow((((sqrt(Rg2)*q0)/b)),((-1.0) - 3.0/miu)))/miu)) - (2.0*C2*sqrt(Rg2)*pow((((sqrt(Rg2)*q0)/b)),((-1.0) - 2.0/miu)))/miu - (C1*sqrt(Rg2)*pow((((sqrt(Rg2)*q0)/b)),((-1.0) - 1.0/miu)))/miu));
    
    t12 = ((1.0 + tanh(((-C4) + (sqrt(Rg2)*q0)/b)/C5)));
    
    t13 = (b*C*((4.0/15.0 - pow(E,(-((q02*Rg2)/b2)))*((11.0/15.0 + (7.0*b2)/(15.0*q02* Rg2))) + (7.0*b2)/(15.0*q02*Rg2))));
    
    t14 = (2.0*b4*(((-1.0) + pow(E,(-((q02*Rg2)/b2))) + (q02*Rg2)/b2))*((1.0 + 1.0/2.0*(((-1.0) - tanh(((-C4) + (sqrt(Rg2)*q0)/b)/C5))))));
    
    t15 = ((C3*pow((((sqrt(Rg2)*q0)/b)),((-3.0)/miu)) + C2*pow((((sqrt(Rg2)*q0)/b)),((-2.0)/miu)) + C1*pow((((sqrt(Rg2)*q0)/b)),((-1.0)/miu))));
	
    
    yy = (pow(q0,p1)*(((-((b*pi)/(L*q0))) +t1/L +t2/(q04*Rg22) + 1.0/2.0*t3*t4)) + (t5*((pow(q0,(p1 - p2))*(((-pow(q0,(-p1)))*(((b2*pi)/(L*q02) +t6/L +t7/(2.0*C5) -t8/(C5*q04*Rg22) +t9/(q04*Rg22) -t10/(q05*Rg22) + 1.0/2.0*t11*t12)) - b*p1*pow(q0,((-1.0) - p1))*(((-((b*pi)/(L*q0))) +t13/L +t14/(q04*Rg22) + 1.0/2.0*t15*((1.0 + tanh(((-C4) + (sqrt(Rg2)*q0)/b)/C5)))))))))));
	
    return (yy);
}



///////////////

//
//     FUNCTION gfn2:    CONTAINS F(Q,A,B,mu)**2  AS GIVEN
//                       BY (53) AND (56,57) IN CHEN AND 
//                       KOTLARCHYK REFERENCE
//
//     <PROLATE ELLIPSOIDS>
//
double
gfn2(double xx, double crmaj, double crmin, double trmaj, double trmin, double delpc, double delps, double qq)
{
	// local variables
	double aa,bb,u2,ut2,uq,ut,vc,vt,gfnc,gfnt,gfn2,pi43,gfn,Pi;
	
	Pi = 4.0*atan(1.0);
	
	pi43=4.0/3.0*Pi;
	aa = crmaj;
	bb = crmin;
	u2 = (aa*aa*xx*xx + bb*bb*(1.0-xx*xx));
	ut2 = (trmaj*trmaj*xx*xx + trmin*trmin*(1.0-xx*xx));
	uq = sqrt(u2)*qq;
	ut= sqrt(ut2)*qq;
	vc = pi43*aa*bb*bb;
	vt = pi43*trmaj*trmin*trmin;
	gfnc = 3.0*(sin(uq)/uq/uq - cos(uq)/uq)/uq*vc*delpc;
	gfnt = 3.0*(sin(ut)/ut/ut - cos(ut)/ut)/ut*vt*delps;
	gfn = gfnc+gfnt;
	gfn2 = gfn*gfn;
	
	return (gfn2);
}

//
//     FUNCTION gfn4:    CONTAINS F(Q,A,B,MU)**2  AS GIVEN
//                       BY (53) & (58-59) IN CHEN AND
//                       KOTLARCHYK REFERENCE
//
//       <OBLATE ELLIPSOID>
// function gfn4 for oblate ellipsoids 
double
gfn4(double xx, double crmaj, double crmin, double trmaj, double trmin, double delpc, double delps, double qq)
{
	// local variables
	double aa,bb,u2,ut2,uq,ut,vc,vt,gfnc,gfnt,tgfn,gfn4,pi43,Pi;
	
	Pi = 4.0*atan(1.0);
	pi43=4.0/3.0*Pi;
  	aa = crmaj;
 	bb = crmin;
 	u2 = (bb*bb*xx*xx + aa*aa*(1.0-xx*xx));
 	ut2 = (trmin*trmin*xx*xx + trmaj*trmaj*(1.0-xx*xx));
   	uq = sqrt(u2)*qq;
 	ut= sqrt(ut2)*qq;
	vc = pi43*aa*aa*bb;
   	vt = pi43*trmaj*trmaj*trmin;
   	gfnc = 3.0*(sin(uq)/uq/uq - cos(uq)/uq)/uq*vc*delpc;
  	gfnt = 3.0*(sin(ut)/ut/ut - cos(ut)/ut)/ut*vt*delps;
  	tgfn = gfnc+gfnt;
  	gfn4 = tgfn*tgfn;
  	
  	return (gfn4);
}

double
FlePolyLen_kernel(double q, double radius, double length, double lb, double zz, double delrho, double zi)
{
    double Pq,vcyl,dl;
    double Pi,qr;
    
    Pi = 4.0*atan(1.0);
    qr = q*radius;
    
    Pq = Sk_WR(q,zi,lb);		//does not have cross section term
    Pq *= (2.0*NR_BessJ1(qr)/qr)*(2.0*NR_BessJ1(qr)/qr);
    
    vcyl=Pi*radius*radius*zi;
    Pq *= vcyl*vcyl;
    
    dl = SchulzPoint_cpr(zi,length,zz);
    return (Pq*dl);	
	
}

double
FlePolyRad_kernel(double q, double ravg, double Lc, double Lb, double zz, double delrho, double zi)
{
    double Pq,vcyl,dr;
    double Pi,qr;
    
    Pi = 4.0*atan(1.0);
    qr = q*zi;
    
    Pq = Sk_WR(q,Lc,Lb);		//does not have cross section term
    Pq *= (2.0*NR_BessJ1(qr)/qr)*(2.0*NR_BessJ1(qr)/qr);
    
    vcyl=Pi*zi*zi*Lc;
    Pq *= vcyl*vcyl;
    
    dr = SchulzPoint_cpr(zi,ravg,zz);
    return (Pq*dr);	
	
}

double
CSCylIntegration(double qq, double rad, double radthick, double facthick, double rhoc, double rhos, double rhosolv, double length)
{
	double answer,halfheight,Pi;
	double lolim,uplim,summ,yyy,zi;
	int nord,i;
	
	// set up the integration end points 
	Pi = 4.0*atan(1.0);
	nord = 76;
	lolim = 0;
	uplim = Pi/2;
	halfheight = length/2.0;
	
	summ = 0.0;				// initialize integral
	i=0;
	for(i=0;i<nord;i++) {
		zi = ( Gauss76Z[i]*(uplim-lolim) + uplim + lolim )/2.0;
		yyy = Gauss76Wt[i] * CScyl(qq, rad, radthick, facthick, rhoc,rhos,rhosolv, halfheight, zi);
		summ += yyy;
	}
	
	// calculate value of integral to return
	answer = (uplim-lolim)/2.0*summ;
	return (answer);
}

double
CScyl(double qq, double rad, double radthick, double facthick, double rhoc, double rhos, double rhosolv, double length, double dum)
{	
	// qq is the q-value for the calculation (1/A)
	// radius is the core radius of the cylinder (A)
	//  radthick and facthick are the radial and face layer thicknesses
	// rho(n) are the respective SLD's
	// length is the *Half* CORE-LENGTH of the cylinder 
	// dum is the dummy variable for the integration (theta)
	
	double dr1,dr2,besarg1,besarg2,vol1,vol2,sinarg1,sinarg2,t1,t2,retval;
	double Pi;
	
	Pi = 4.0*atan(1.0); 
	
	dr1 = rhoc-rhos;
	dr2 = rhos-rhosolv;
	vol1 = Pi*rad*rad*(2.0*length);
	vol2 = Pi*(rad+radthick)*(rad+radthick)*(2.0*length+2.0*facthick);
	
	besarg1 = qq*rad*sin(dum);
	besarg2 = qq*(rad+radthick)*sin(dum);
	sinarg1 = qq*length*cos(dum);
	sinarg2 = qq*(length+facthick)*cos(dum);
	
	t1 = 2.0*vol1*dr1*sin(sinarg1)/sinarg1*NR_BessJ1(besarg1)/besarg1;
	t2 = 2.0*vol2*dr2*sin(sinarg2)/sinarg2*NR_BessJ1(besarg2)/besarg2;
	
	retval = ((t1+t2)*(t1+t2))*sin(dum);
	return (retval);
    
}


double
CoreShellCylKernel(double qq, double rcore, double thick, double rhoc, double rhos, double rhosolv, double length, double dum)
{
	
    double dr1,dr2,besarg1,besarg2,vol1,vol2,sinarg1,sinarg2,t1,t2,retval;
    double Pi;
    
    Pi = 4.0*atan(1.0);
    
    dr1 = rhoc-rhos;
    dr2 = rhos-rhosolv;
    vol1 = Pi*rcore*rcore*(2.0*length);
    vol2 = Pi*(rcore+thick)*(rcore+thick)*(2.0*length+2.0*thick);
    
    besarg1 = qq*rcore*sin(dum);
    besarg2 = qq*(rcore+thick)*sin(dum);
    sinarg1 = qq*length*cos(dum);
    sinarg2 = qq*(length+thick)*cos(dum);
    
    t1 = 2.0*vol1*dr1*sin(sinarg1)/sinarg1*NR_BessJ1(besarg1)/besarg1;
    t2 = 2.0*vol2*dr2*sin(sinarg2)/sinarg2*NR_BessJ1(besarg2)/besarg2;
    
    retval = ((t1+t2)*(t1+t2))*sin(dum);
	
    return (retval);
}

double
Cyl_PolyLenKernel(double q, double radius, double len_avg, double zz, double delrho, double dumLen)
{
	
    double halfheight,uplim,lolim,zi,summ,yyy,Pi;
    double answer,dr,Vcyl;
    int i,nord;
    
    Pi = 4.0*atan(1.0);
    lolim = 0;
    uplim = Pi/2.0;
    halfheight = dumLen/2.0;
    nord=20;
    summ = 0.0;
    
    //do the cylinder orientational average
    for(i=0;i<nord;i++) {
		zi = ( Gauss20Z[i]*(uplim-lolim) + uplim + lolim )/2.0;
		yyy = Gauss20Wt[i] * CylKernel(q, radius, halfheight, zi);
		summ += yyy;
    }
    answer = (uplim-lolim)/2.0*summ;
    // Multiply by contrast^2
    answer *= delrho*delrho;
    // don't do the normal scaling to volume here
    // instead, multiply by VCyl^2 to get rid of the normalization for this radius of cylinder
    Vcyl = Pi*radius*radius*dumLen;
    answer *= Vcyl*Vcyl;
    
    dr = SchulzPoint_cpr(dumLen,len_avg,zz);
    return(dr*answer);
}


double
Stackdisc_kern(double qq, double rcore, double rhoc, double rhol, double rhosolv, double length, double thick, double dum, double gsd, double d, double N)
{         	
	// qq is the q-value for the calculation (1/A)
	// rcore is the core radius of the cylinder (A)
	// rho(n) are the respective SLD's
	// length is the *Half* CORE-LENGTH of the cylinder = L (A)
	// dum is the dummy variable for the integration (x in Feigin's notation)
	
	//Local variables 
	double totald,dr1,dr2,besarg1,besarg2,area,sinarg1,sinarg2,t1,t2,retval,sqq,dexpt;
	double Pi;
	int kk;
	
	Pi = 4.0*atan(1.0);
	
	dr1 = rhoc-rhosolv;
	dr2 = rhol-rhosolv;
	area = Pi*rcore*rcore;
	totald=2.0*(thick+length);
	
	besarg1 = qq*rcore*sin(dum);
	besarg2 = qq*rcore*sin(dum);
	
	sinarg1 = qq*length*cos(dum);
	sinarg2 = qq*(length+thick)*cos(dum);
	
	t1 = 2*area*(2*length)*dr1*(sin(sinarg1)/sinarg1)*(NR_BessJ1(besarg1)/besarg1);
	t2 = 2*area*dr2*(totald*sin(sinarg2)/sinarg2-2*length*sin(sinarg1)/sinarg1)*(NR_BessJ1(besarg2)/besarg2);
	
	retval =((t1+t2)*(t1+t2))*sin(dum);
	
	// loop for the structure facture S(q)
	sqq=0.0;
	for(kk=1;kk<N;kk+=1) {
		dexpt=qq*cos(dum)*qq*cos(dum)*d*d*gsd*gsd*kk/2.0;
		sqq=sqq+(N-kk)*cos(qq*cos(dum)*d*kk)*exp(-1.*dexpt);
	}			
	
	// end of loop for S(q)
	sqq=1.0+2.0*sqq/N;
	retval *= sqq;
    
	return(retval);
}


double
Cyl_PolyRadKernel(double q, double radius, double length, double zz, double delrho, double dumRad)
{
	
    double halfheight,uplim,lolim,zi,summ,yyy,Pi;
    double answer,dr,Vcyl;
    int i,nord;
    
    Pi = 4.0*atan(1.0);
    lolim = 0;
    uplim = Pi/2.0;
    halfheight = length/2.0;
	//    nord=20;
    nord=76;
    summ = 0.0;
    
    //do the cylinder orientational average
	//    for(i=0;i<nord;i++) {
	//            zi = ( Gauss20Z[i]*(uplim-lolim) + uplim + lolim )/2.0;
	//            yyy = Gauss20Wt[i] * CylKernel(q, dumRad, halfheight, zi);
	//            summ += yyy;
	//    }
    for(i=0;i<nord;i++) {
		zi = ( Gauss76Z[i]*(uplim-lolim) + uplim + lolim )/2.0;
		yyy = Gauss76Wt[i] * CylKernel(q, dumRad, halfheight, zi);
		summ += yyy;
    }
    answer = (uplim-lolim)/2.0*summ;
    // Multiply by contrast^2
    answer *= delrho*delrho;
    // don't do the normal scaling to volume here
    // instead, multiply by VCyl^2 to get rid of the normalization for this radius of cylinder
    Vcyl = Pi*dumRad*dumRad*length;
    answer *= Vcyl*Vcyl;
    
    dr = SchulzPoint_cpr(dumRad,radius,zz);
    return(dr*answer);
}

double
SchulzPoint_cpr(double dumRad, double radius, double zz)
{
    double dr;
    
    dr = zz*log(dumRad) - gammaln(zz+1.0) + (zz+1.0)*log((zz+1.0)/radius)-(dumRad/radius*(zz+1.0));
    return(exp(dr));
}

static double
gammaln(double xx)
{
	double x,y,tmp,ser;
	static double cof[6]={76.18009172947146,-86.50532032941677,
		24.01409824083091,-1.231739572450155,
		0.1208650973866179e-2,-0.5395239384953e-5};
	int j;
	
	y=x=xx;
	tmp=x+5.5;
	tmp -= (x+0.5)*log(tmp);
	ser=1.000000000190015;
	for (j=0;j<=5;j++) ser += cof[j]/++y;
	return -tmp+log(2.5066282746310005*ser/x);
}


double
EllipsoidKernel(double qq, double a, double nua, double dum)
{
    double arg,nu,retval;		//local variables
	
    nu = nua/a;
    arg = qq*a*sqrt(1+dum*dum*(nu*nu-1));
    
    retval = (sin(arg)-arg*cos(arg))/(arg*arg*arg);
    retval *= retval;
    retval *= 9;
    
    return(retval);
}//Function EllipsoidKernel()

double
HolCylKernel(double qq, double rcore, double rshell, double length, double dum)
{
    double gamma,arg1,arg2,lam1,lam2,psi,sinarg,t2,retval;		//local variables
    
    gamma = rcore/rshell;
    arg1 = qq*rshell*sqrt(1-dum*dum);		//1=shell (outer radius)
    arg2 = qq*rcore*sqrt(1-dum*dum);			//2=core (inner radius)
    lam1 = 2*NR_BessJ1(arg1)/arg1;
    lam2 = 2*NR_BessJ1(arg2)/arg2;
    psi = 1/(1-gamma*gamma)*(lam1 -  gamma*gamma*lam2);		//SRK 10/19/00
    
    sinarg = qq*length*dum/2;
    t2 = sin(sinarg)/sinarg;
    
    retval = psi*psi*t2*t2;
    
    return(retval);
}//Function HolCylKernel()

double
PPKernel(double aa, double mu, double uu)
{
    // mu passed in is really mu*sqrt(1-sig^2)
    double arg1,arg2,Pi,tmp1,tmp2;			//local variables
	
    Pi = 4.0*atan(1.0);
    
    //handle arg=0 separately, as sin(t)/t -> 1 as t->0
    arg1 = (mu/2)*cos(Pi*uu/2);
    arg2 = (mu*aa/2)*sin(Pi*uu/2);
    if(arg1==0) {
		tmp1 = 1;
	} else {
		tmp1 = sin(arg1)*sin(arg1)/arg1/arg1;
    }
    
    if (arg2==0) {
		tmp2 = 1;
	} else {
		tmp2 = sin(arg2)*sin(arg2)/arg2/arg2;
    }
	
    return (tmp1*tmp2);
	
}//Function PPKernel()


double
TriaxialKernel(double q, double aa, double bb, double cc, double dx, double dy)
{
	
    double arg,val,pi;			//local variables
	
    pi = 4.0*atan(1.0);
    
    arg = aa*aa*cos(pi*dx/2)*cos(pi*dx/2);
    arg += bb*bb*sin(pi*dx/2)*sin(pi*dx/2)*(1-dy*dy);
    arg += cc*cc*dy*dy;
    arg = q*sqrt(arg);
    val = 9 * ( (sin(arg) - arg*cos(arg))/(arg*arg*arg) ) * ( (sin(arg) - arg*cos(arg))/(arg*arg*arg) );
    
    return (val);
	
}//Function TriaxialKernel()


double
CylKernel(double qq, double rr,double h, double theta)
{
	
	// qq is the q-value for the calculation (1/A)
	// rr is the radius of the cylinder (A)
	// h is the HALF-LENGTH of the cylinder = L/2 (A)
	
    double besarg,bj,retval,d1,t1,b1,t2,b2;		 //Local variables 
	
	
    besarg = qq*rr*sin(theta);
	
    bj =NR_BessJ1(besarg);
	
	//* Computing 2nd power */
    d1 = sin(qq * h * cos(theta));
    t1 = d1 * d1;
	//* Computing 2nd power */
    d1 = bj;
    t2 = d1 * d1 * 4.0 * sin(theta);
	//* Computing 2nd power */
    d1 = qq * h * cos(theta);
    b1 = d1 * d1;
	//* Computing 2nd power */
    d1 = qq * rr * sin(theta);
    b2 = d1 * d1;
    retval = t1 * t2 / b1 / b2;
	
    return (retval);
	
}//Function CylKernel()

double
EllipCylKernel(double qq, double ra,double nu, double theta)
{
	//this is the function LAMBDA1^2 in Feigin's notation	
	// qq is the q-value for the calculation (1/A)
	// ra is the transformed radius"a" in Feigin's notation
	// nu is the ratio (major radius)/(minor radius) of the Ellipsoid [=] ---
	// theta is the dummy variable of the integration
	
	double retval,arg;		 //Local variables 
	
	arg = qq*ra*sqrt((1+nu*nu)/2+(1-nu*nu)*cos(theta)/2);
	
	retval = 2*NR_BessJ1(arg)/arg;
	
	//square it
	retval *= retval;
	
    return(retval);
	
}//Function EllipCylKernel()

double NR_BessJ1(double x)
{
	double ax,z;
	double xx,y,ans,ans1,ans2;
	
	if ((ax=fabs(x)) < 8.0) {
		y=x*x;
		ans1=x*(72362614232.0+y*(-7895059235.0+y*(242396853.1
												  +y*(-2972611.439+y*(15704.48260+y*(-30.16036606))))));
		ans2=144725228442.0+y*(2300535178.0+y*(18583304.74
											   +y*(99447.43394+y*(376.9991397+y*1.0))));
		ans=ans1/ans2;
	} else {
		z=8.0/ax;
		y=z*z;
		xx=ax-2.356194491;
		ans1=1.0+y*(0.183105e-2+y*(-0.3516396496e-4
								   +y*(0.2457520174e-5+y*(-0.240337019e-6))));
		ans2=0.04687499995+y*(-0.2002690873e-3
							  +y*(0.8449199096e-5+y*(-0.88228987e-6
													 +y*0.105787412e-6)));
		ans=sqrt(0.636619772/ax)*(cos(xx)*ans1-z*sin(xx)*ans2);
		if (x < 0.0) ans = -ans;
	}
	
	return(ans);
}
