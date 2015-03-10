INCLUDE "shmem.fh"

INTEGER PSYNC(SHMEM_REDUCE_SYNC_SIZE)
DATA PSYNC /SHMEM_REDUCE_SYNC_SIZE*SHMEM_SYNC_VALUE/
PARAMETER (NR=1)
INTEGER*4 PWRK(MAX(NR/2+1,SHMEM_REDUCE_MIN_WRKDATA_SIZE))
INTEGER FOO, FOOAND
SAVE FOO, FOOAND, PWRK
INTRINSIC SHMEM_MY_PE()

FOO = SHMEM_MY_PE()
IF ( MOD(SHMEM_MY_PE() .EQ. 0) THEN
    IF ( MOD(SHMEM_N_PES()(),2) .EQ. 0) THEN
       CALL SHMEM_INT8_AND_TO_ALL(FOOAND, FOO, NR, 0, 1, NPES/2, &
	 PWRK, PSYNC)
    ELSE
       CALL SHMEM_INT8_AND_TO_ALL(FOOAND, FOO, NR, 0, 1, NPES/2+1, &
	 PWRK, PSYNC)
   
    ENDIF
    PRINT*,'Result on PE ',SHMEM_MY_PE(),' is ',FOOAND
ENDIF