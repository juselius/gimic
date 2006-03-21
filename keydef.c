/*
 * $Id$
 *
 */

#include <getkw.h>

BEGIN_SECTION(grid_opt)
	KEYWORD("type", STRING, OPTIONAL)
	KEYWORD("origin", DBL_ARRAY, REQUIRED)
	KEYWORD("v1", DBL_ARRAY, REQUIRED)
	KEYWORD("v2", DBL_ARRAY, REQUIRED)
	KEYWORD("step", DBL_ARRAY, OPTIONAL)
	KEYWORD("map", DBL_ARRAY, OPTIONAL)
	KEYWORD("height", DBL_ARRAY, OPTIONAL)
	KEYWORD("width", DBL_ARRAY, OPTIONAL)
	KEYWORD("l3", DOUBLE, OPTIONAL)
	KEYWORD("radius", DOUBLE, OPTIONAL)
	KEYWORD("gridplot", INT, OPTIONAL)
END_SECTION

BEGIN_SECTION(intgrid_opt)
	KEYWORD("type", STRING, OPTIONAL)
	KEYWORD("origin", DBL_ARRAY, REQUIRED)
	KEYWORD("v1", DBL_ARRAY, REQUIRED)
	KEYWORD("v2", DBL_ARRAY, REQUIRED)
	KEYWORD("step", DBL_ARRAY, OPTIONAL)
	KEYWORD("map", DBL_ARRAY, OPTIONAL)
	KEYWORD("height", DBL_ARRAY, OPTIONAL)
	KEYWORD("width", DBL_ARRAY, OPTIONAL)
	KEYWORD("l3", DOUBLE, OPTIONAL)
	KEYWORD("radius", DOUBLE, OPTIONAL)
	KEYWORD("gridplot", INT, OPTIONAL)
	KEYWORD("gauss_points", INT_ARRAY, REQUIRED)
	KEYWORD("grid_points", INT_ARRAY, REQUIRED)
END_SECTION

BEGIN_SECTION(divgrid_opt)
	KEYWORD("type", STRING, OPTIONAL)
	KEYWORD("origin", DBL_ARRAY, REQUIRED)
	KEYWORD("v1", DBL_ARRAY, REQUIRED)
	KEYWORD("v2", DBL_ARRAY, REQUIRED)
	KEYWORD("step", DBL_ARRAY, OPTIONAL)
	KEYWORD("map", DBL_ARRAY, OPTIONAL)
	KEYWORD("height", DBL_ARRAY, OPTIONAL)
	KEYWORD("width", DBL_ARRAY, OPTIONAL)
	KEYWORD("l3", DOUBLE, OPTIONAL)
	KEYWORD("radius", DOUBLE, OPTIONAL)
	KEYWORD("gridplot", INT, OPTIONAL)
END_SECTION

BEGIN_SECTION(egrid_opt)
	KEYWORD("type", STRING, OPTIONAL)
	KEYWORD("origin", DBL_ARRAY, REQUIRED)
	KEYWORD("v1", DBL_ARRAY, REQUIRED)
	KEYWORD("v2", DBL_ARRAY, REQUIRED)
	KEYWORD("step", DBL_ARRAY, OPTIONAL)
	KEYWORD("map", DBL_ARRAY, OPTIONAL)
	KEYWORD("height", DBL_ARRAY, OPTIONAL)
	KEYWORD("width", DBL_ARRAY, OPTIONAL)
	KEYWORD("l3", DOUBLE, OPTIONAL)
	KEYWORD("radius", DOUBLE, OPTIONAL)
	KEYWORD("gridplot", INT, OPTIONAL)
END_SECTION

BEGIN_SECTION(integral_opt)
	KEYWORD("interpolate", INT, OPTIONAL)
	KEYWORD("lip_order", INT, OPTIONAL)
	KEYWORD("radius", DOUBLE, OPTIONAL)
	KEYWORD("tensor", INT, OPTIONAL)
	SECTION("grid", STRING, HAS_ARG|REQUIRED,intgrid_opt)
END_SECTION

BEGIN_SECTION(divj_opt)
	KEYWORD("plots", INT_ARRAY, OPTIONAL)
	KEYWORD("gopenmol", STRING, OPTIONAL)
	SECTION("grid", STRING, HAS_ARG|OPTIONAL,divgrid_opt)
END_SECTION

BEGIN_SECTION(edens_opt)
	KEYWORD("mos", INT_ARRAY, OPTIONAL)
	KEYWORD("mofile", STRING, OPTIONAL)
	KEYWORD("plots", INT_ARRAY, OPTIONAL)
	KEYWORD("gopenmol", STRING, OPTIONAL)
	SECTION("grid", STRING, HAS_ARG|OPTIONAL,egrid_opt)
END_SECTION

BEGIN_SECTION(plot_opt)
	KEYWORD("plots", INT_ARRAY, OPTIONAL)
	KEYWORD("vector", STRING, OPTIONAL)
	KEYWORD("modulus", STRING, OPTIONAL)
	KEYWORD("nvector", STRING, OPTIONAL)
	KEYWORD("projection", STRING, OPTIONAL)
	KEYWORD("gopenmol", STRING, OPTIONAL)
END_SECTION

BEGIN_SECTION(cdens_opt)
	KEYWORD("magnet", DBL_ARRAY, OPTIONAL)
	KEYWORD("orthogonal_magnet", INT, OPTIONAL)
	KEYWORD("zpoint", INT, OPTIONAL)
	KEYWORD("gopenmol", STRING, OPTIONAL)
	KEYWORD("jtensor", STRING, OPTIONAL)
	KEYWORD("jvector", STRING, OPTIONAL)
	KEYWORD("diamag", INT, OPTIONAL)
	KEYWORD("paramag", INT, OPTIONAL)
	KEYWORD("scale_vectors", DOUBLE, OPTIONAL)
	SECTION("plot", INT, HAS_ARG|OPTIONAL,plot_opt)
END_SECTION

BEGIN_SECTION(cdef_opt)
	KEYWORD("title", STRING, OPTIONAL)
	KEYWORD("basis", STRING, REQUIRED)
	KEYWORD("density", STRING, REQUIRED)
	KEYWORD("spherical", INT, OPTIONAL)
	KEYWORD("rerun", INT, OPTIONAL)
	KEYWORD("mpirun", INT, OPTIONAL)
	KEYWORD("debug", INT, OPTIONAL)
	KEYWORD("calc", STR_ARRAY, REQUIRED)
	SECTION("grid", STRING, HAS_ARG|REQUIRED,grid_opt)
	SECTION("cdens", EMPTY, OPTIONAL,cdens_opt)
	SECTION("integral", EMPTY, OPTIONAL,integral_opt)
	SECTION("divj", EMPTY, OPTIONAL,divj_opt)
	SECTION("edens", EMPTY, OPTIONAL,edens_opt)
END_SECTION

BEGIN_SECTION(sections)
	SECTION("CDENS", EMPTY, REQUIRED,cdef_opt)
END_SECTION

MAIN_SECTION(sections)
