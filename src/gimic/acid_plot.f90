module acidplot_module
     use globals_module
     use teletype_module
     use settings_module
     use acid_module
     use grid_class
     !use jfield_class <-- this usage causes trouble
    implicit none

    contains
    subroutine acid_cube_plot(grid, tens)
    type(grid_t) :: grid
    integer(I4), dimension(3) :: npts
    integer(I4) :: fd1, i, j, k, l, m
    real(DP), dimension(:,:) :: tens
    real(DP), dimension(3) :: qmin, qmax, step, r 
    real(DP) :: val, maxi, mini

    ! collect grid information
    call get_grid_size(grid, npts(1), npts(2), npts(3))
    qmin = gridpoint(grid, 1, 1, 1)
    qmax = gridpoint(grid, npts(1), npts(2), npts(3))
    step = (qmax - qmin)/(npts - 1)
    !                           origin step number of points
    ! no access to original opencube function
    ! fd1 = opencube('acid.cube', qmin, step, npts)
    
     call getfd(fd1)
     if (fd1 == 0) then
         stop 1
     end if

     open(unit=fd1,file='acid.cube',form='formatted', status='unknown')
     write(fd1,*) 'Gaussian cube data, generated by genpot'
     write(fd1,*) 
     write(fd1, '(i5,3f12.6)') 0, qmin
     write(fd1, '(i5,3f12.6)') npts(1), step(1), 0.d0, 0.d0
     write(fd1, '(i5,3f12.6)') npts(2), 0.d0, step(2), 0.d0
     write(fd1, '(i5,3f12.6)') npts(3), 0.d0, 0.d0, step(3)

    maxi = 0.0d0
    mini = 0.0d0
    l = 0
    m = 0
    do i = 1, npts(1)
        do j = 1, npts(2)
            do k = 1, npts(3)
                m = m + 1
                r = gridpoint(grid, i, j, k)
                ! maybe better to call ctens here ?? check code !
                val = get_acid(r, tens(:,m))  
                if (val > maxi) maxi = val 
                if (val > mini) mini = val 
                if (fd1 /= 0) then
                    write(fd1,'(f12.6)',advance='no') val
                    if (mod(l,6) == 5) write(fd1,*)
                end if
                l = l + 1
            end do
        end do
    end do
    print *, 'ACID: maxi, mini', maxi, mini

    call closefd(fd1)
    end subroutine

end module

! vim:et:sw=4:ts=4
