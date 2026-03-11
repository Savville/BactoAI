import ftplib

try:
    print("Connecting via FTPS...")
    ftps = ftplib.FTP_TLS('ftp.bvbrc.org')
    ftps.login()
    ftps.prot_p() # Ensure data connection is also secure
    print("Logged in successfully.")
    
    # Change directory
    ftps.cwd('/patric2/current_release/RELEASE_NOTES/')
    print("Listing files in directory...")
    # ftps.retrlines('LIST')
    
    with open('test_PATRIC.txt', 'wb') as fp:
        ftps.retrbinary('RETR PATRIC_genomes_AMR.txt', fp.write, blocksize=8192)
    print("Downloaded successfully.")
    ftps.quit()
except Exception as e:
    print(f"Error: {e}")
