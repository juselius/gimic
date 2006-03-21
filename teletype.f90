!
! $Id$
!

module teletype_m
	use precision_m
	implicit none

	integer(I4), parameter :: STDOUT=6
	integer(I4), parameter :: STDERR=0
	integer(I4), parameter :: DEVNULL=-1

	character(160) :: str_g 
	private ttunit, level

	integer(I4), parameter :: NONSTDOUT=7
	integer(I4) :: ttunit=6
	integer(I4) :: level=0
contains
	subroutine msg_out(str)
		character(*), intent(in) :: str

		if (ttunit == DEVNULL) return
		
		write(ttunit, 100) trim(str)
100 format(x,a)	
	end subroutine

	subroutine msg_note(str)
		character(*), intent(in) :: str

		if (ttunit == DEVNULL) return

		write(ttunit, 100) ' *** ', trim(str)
100 format(a,a)	
	end subroutine
	
	subroutine msg_info(str)
		character(*), intent(in) :: str

		if (ttunit == DEVNULL) return

		write(ttunit, 100) ' INFO: ', trim(str)
100 format(a,a)	
	end subroutine

	subroutine msg_warn(str)
		character(*), intent(in) :: str

		if (ttunit == DEVNULL) return

		write(ttunit, 100) ' WARNING: ', trim(str)
100 format(a,a)	
	end subroutine

	subroutine msg_debug(str, l)
		character(*), intent(in) :: str
		integer(I4) :: l

		if (level == 0) return
		if (l > level) return

		write(STDOUT, 100) ' DEBUG: ', trim(str)
100 format(a,a)	
	end subroutine

	subroutine msg_error(str)
		character(*), intent(in) :: str

		write(STDERR, 102) '<<< ERROR: ', trim(str), ' >>>'

100 format(a)	
101 format(x,a)	
102 format(a,a,a)	
	end subroutine

	subroutine msg_critical(str)
		character(*), intent(in) :: str

		write(STDERR, 101) repeat('>', 70)
		write(STDERR, 100) ' <'
		write(STDERR, 102) ' < ', trim(str)
		write(STDERR, 100) ' <'
		write(STDERR, 101) repeat('>', 70)

100 format(a)	
101 format(x,a)	
102 format(a,a)	
	end subroutine

	subroutine nl
		if (ttunit == DEVNULL) return

		write(ttunit, *) 
	end subroutine

	subroutine set_teletype_unit(u)
		integer(I4), intent(in) :: u
		ttunit=u
	end subroutine

	subroutine get_teletype_unit(u)
		integer(I4), intent(out) :: u
		u=ttunit
	end subroutine 

	subroutine set_debug_level(l)
		integer(I4), intent(in) :: l
		level=l
	end subroutine 

	subroutine get_debug_level(l)
		integer(I4), intent(out) :: l
		l=level
	end subroutine 

	subroutine disable_stdout()
		logical :: o_p

		inquire(STDOUT,opened=o_p)
		if (o_p) then
			close(STDOUT)
		end if
		open(STDOUT, file='/dev/null')

		inquire(NONSTDOUT,opened=o_p)
		if (.not. o_p) then
			open(NONSTDOUT, file='/dev/stdout')
		end if

		if ( ttunit == STDOUT ) then
			ttunit=NONSTDOUT
		end if
	end subroutine
	
	subroutine enable_stdout()
		logical :: o_p

		inquire(NONSTDOUT,opened=o_p)
		if (o_p) then
			close(NONSTDOUT)
		end if

		inquire(STDOUT,opened=o_p)
		if (.not. o_p) then
			open(STDOUT, file='/dev/stdout')
		end if

		if ( ttunit == NONSTDOUT ) then
			ttunit=STDOUT
		end if
	end subroutine
end module
