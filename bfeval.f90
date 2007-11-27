!
! Basis function evaluator
!

module bfeval_m
	use globals_m
	use basis_m
	use gtodefs_m
	use caos_m
	use cao2sao_m
	implicit none

	public bfeval, init_bfeval, del_bfeval, bfeval_t

	type bfeval_t
		type(molecule_t), pointer :: mol
		real(DP), dimension(:), pointer :: bf
		real(DP), dimension(:), pointer :: sbf
		real(DP), dimension(3) :: r
	end type

	private
	
	integer(I4) :: i, j, k, natoms, nctr, ncomp, nccomp, idx
	type(atom_t), pointer :: atom
	type(basis_t), pointer :: basis
	type(contraction_t), pointer :: ctr
	real(DP), dimension(3) :: rr, coord
		
contains

	subroutine init_bfeval(bfv, mol)
		type(bfeval_t) :: bfv
		type(molecule_t), target :: mol

		if (associated(bfv%bf)) then
			call msg_warn('init_bfeval(): already allocated!')
		else
			allocate(bfv%bf(get_ncgto(mol)))
			if (spherical) allocate(bfv%sbf(get_nccgto(mol)))
		end if
		bfv%mol=>mol
		bfv%r=INITRV
	end subroutine

	subroutine del_bfeval(bfv)
		type(bfeval_t) :: bfv
		if (associated(bfv%bf)) then
			deallocate(bfv%bf)
			if (spherical) deallocate(bfv%sbf)
			nullify(bfv%bf)
			nullify(bfv%sbf)
			nullify(bfv%mol)
		else
			call msg_warn('del_bfeval(): not allocated!')
		end if
	end subroutine
	
	subroutine bfeval(bfv, r, ans)
		type(bfeval_t) :: bfv
		real(DP), dimension(3), intent(in) :: r
		real(DP), dimension(:), pointer :: ans

		integer(I4), dimension(99) :: posvec
		integer(I4) :: idx1, idx2

		! Check if we already have the result
		if (r(1)==bfv%r(1) .and. r(2)==bfv%r(2) .and. r(3)==bfv%r(3)) then 
			ans=>bfv%bf
			return
		end if
		
		bfv%r=r
		natoms=get_natoms(bfv%mol)
		
		idx=1
		idx2=0
		bfv%bf=0.d0
		do i=1,natoms
			call get_atom(bfv%mol,i,atom)
			call get_coord(atom, coord)
			call get_basis(atom, basis)
			rr=r-coord
!            nctr=get_nctr(basis)
			call filter_screened(basis, rr, posvec, nctr)
			do k=1,nctr 
				j=posvec(k)
				call get_contraction(atom, j, ctr)
!                nccomp=get_nccomp(ctr)
				idx=idx2+get_ctridx(basis, j)
!                print *, idx, idx1
				call cgto(rr, ctr, bfv%bf(idx:))
!                idx=idx+nccomp
			end do
			idx2=idx2+get_ncgto(basis)
		end do
		if (spherical) then
			call cao2sao(bfv%mol%c2s, bfv%bf, bfv%sbf)
			ans=>bfv%sbf
		else
			ans=>bfv%bf
		end if
	end subroutine 

end module
