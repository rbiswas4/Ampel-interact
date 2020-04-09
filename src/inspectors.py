#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : ampel-interact/default/tv_loader.py
# License           : BSD-3-Clause
# Author            : jn <jnordin@physik.hu-berlin.de>
# Date              : 04.04.2020
# Last Modified Date: 04.04.2020
# Last Modified By  : jn <jnordin@physik.hu-berlin.de>

from typing import List, Dict
from ampel.base.TransientView import TransientView
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec
from ipywidgets import interactive
import ipywidgets as widgets



class ScanLC():
    """
    A simple way to display the lightcurve stored in a TV.
    """

    def __init__( self, display_props : List[str], display_t2s : List[str]) -> None:
        self.display_props = display_props
        self.display_t2s = display_t2s
        self.ztf_filt_col = {'g': (0.3333333333333333, 0.6588235294117647, 0.40784313725490196),
 'r': (0.7686274509803922, 0.3058823529411765, 0.3215686274509804),
  'i': (0.8, 0.7254901960784313, 0.4549019607843137) }


    def inspect_tv(self, i):
        """
        Visual inspection of SN with id i in the list of transient views (self.inspect_list). 
        Each is evaluated as gold (2), silver (1) or bogus (0) through the keyboard.
        """
    
#        global snnbr
        tv = self.inspect_list[self.snnbr]
        snname = ' '.join(tv.tran_names)

        if i == 'Gold':
            print("Gold, very likely SLSNe: %s %s"%(self.snnbr,snname))
            self.decisions[self.snnbr] = i
            self.snnbr += 1
        elif i == 'Silver':
            print("Silver, possible SLSNe (inspect further) %s %s"%(self.snnbr,snname))
            self.decisions[self.snnbr] = i
            self.snnbr += 1
        elif i == 'Bogus':
            print("Bogus, definitely not interesting: %s %s"%(self.snnbr,snname))
            self.decisions[self.snnbr] = i
            self.snnbr += 1
        elif i == 'GoBack':
            print("I want to scan some more, go back!")
            self.snnbr -= 1
        elif i=='Nothing':
            # Lets do nothing
            pass
    
        # Are we done?
        if self.snnbr==len(self.inspect_list):
            print( "Seems like we are all done.")
            return False
    
        # Reset    
        tv = self.inspect_list[self.snnbr]
        snname = ' '.join(tv.tran_names)
    
        # Lightcurve
        lc = tv.get_lightcurve(tv.get_latest_state())

        # Set up plot
        fig = plt.figure(1,figsize=(14,4), constrained_layout = True)

        #plt.subplot(1,2,1)
        gs = fig.add_gridspec(1, 3)
    
        ax1 = fig.add_subplot(gs[0, :-1])
        plt.title(snname + ' ' + str(self.snnbr+1) + ' out of '+str(len(self.inspect_list)))
    
        # Plot detections
        for filter_id, filter_name in zip([1,2,3],['g','r','i']):
            phot = np.array( lc.get_ntuples(['jd','magpsf','sigmapsf'],upper_limits=False,
                              filters={'attribute':'fid','operator':'==','value':filter_id}) )
            if len(phot)==0:
                continue
            plt.errorbar(phot[:,0],phot[:,1],yerr=phot[:,2],color='k',fmt='.',marker='None')
            plt.plot(phot[:,0],phot[:,1],'o',color=self.ztf_filt_col[filter_name],label=filter_name,ms=12)
        # Plot upper limits
        for filter_id, filter_name in zip([1,2,3],['g','r','i']):
            phot = np.array( lc.get_ntuples(['jd','diffmaglim'],upper_limits=True,
                              filters={'attribute':'fid','operator':'==','value':filter_id}) )
            if len(phot)==0:
                continue
            plt.plot(phot[:,0],phot[:,1],'v',markeredgecolor=self.ztf_filt_col[filter_name],ms=10,markerfacecolor='None')

        
        plt.legend(loc='best')
        plt.xlabel('JD')
        plt.ylabel('Alert mag')
        plt.gca().invert_yaxis()

        # Gather statistics 
        ax2 = fig.add_subplot(gs[0, 2])

        for propcount, aprop in enumerate(self.display_props):
            val = np.mean( lc.get_values(aprop) )
            plt.text(0.1,propcount*0.1,'%s  %.2f'%(aprop,val),horizontalalignment='left',fontsize=15)
    
        plt.axis([0,1,0,len(self.display_props)*0.12])
        plt.axis('off')

        # Show
        plt.show()
    
    
        # Print t2 outputs if selected
        for tvrec in tv.t2records:
            # Check if we want to print this
            if not tvrec.get_t2_unit_id() in self.display_t2s:
                continue
            last_result = tvrec.get_results()[-1]
            print('t2 %s yield %s'%(tvrec.get_t2_unit_id(),last_result['output']))
            if tvrec.info['hasError']:
                print('... warning, t2 associated with error')
    
        self.wiggy.value = 'Nothing'
    
        return (i)


    def get_widget(self):
        return widgets.RadioButtons(
                   options=['Nothing','Gold','Silver', 'Bogus', 'GoBack'],
                   value='Nothing',
                   description='Action:',
                   disabled=False
                   )


    def scan_tvlist(self, tvlist : List[TransientView]) -> Dict[int,str]:
        """
        Visual scan of a list of Transient Views.
        """

        # Define a sample RadioButton
        self.wiggy = self.get_widget()

        # This is just a simple counter of which object 
        self.snnbr = 0
        self.inspect_list = tvlist
        self.decisions = {}
	
	# Just a wrapper function for interactive
        def inspect_tv_interact(i):
            return self.inspect_tv(i)
        

        # Set up an interactive function
        y = interactive(inspect_tv_interact, i = self.wiggy)

        # This is the scanning box! 
        # You have three choices (Nothing is not a choice and GoBack steps lets you go back in order)
        # - Gold: This perfectly matches the target transient
        # - Silver : Possibly a match, probably needs further study.
        # - Bogus : This is clearly not it, no reason to look at again.
        display(y)

        return self.decisions





    def scan(self, tv : TransientView, scaneval : Dict[str,str] ) -> None:

        snname = ' '.join(tv.tran_names)

        # Define a sample RadioButton
        wiggy = widgets.RadioButtons(
            options=['Gold', 'Silver', 'Bogus'],
            value=None,
            description='Scan:',
            disabled=False
        )

        # Request evaluation
        def on_change(handler):
            scaneval[snname] = handler['new']
            wiggy.close()
        wiggy.observe(on_change, names='value')

        display(wiggy)


        return None





    def display_ztf_tv(self, tv : TransientView, fig : plt.figure ) -> None:
        """
        IN DEVELOPMENT.
        Visual inspection of SN with id i in the list of transient views (tvlist). 
        Each is evaluated as gold (2), silver (1) or bogus (0) through the keyboard.
        """
    
        snname = ' '.join(tv.tran_names)
   
        # Lightcurve
        lc = tv.get_lightcurve(tv.get_latest_state())

        # Set up plot
        #gs = fig.add_gridspec(1, 3)
        #gs = gridspec.GridSpec(ncols=3, nrows=1, figure=fig)
        #ax1 = fig.add_subplot(gs[0, :-1])
        #ax1 = fig.add_subplot(gs[0,0:1])
        #ax1 = fig.add_subplot(1,2,1)
        
        plt.title(snname)
    
        # Plot detections
        for filter_id, filter_name in zip([1,2,3],['g','r','i']):
            phot = np.array( lc.get_ntuples(['jd','magpsf','sigmapsf'],upper_limits=False,
                              filters={'attribute':'fid','operator':'==','value':filter_id}) )	

            if len(phot)==0:
                continue
            plt.errorbar(phot[:,0],phot[:,1],yerr=phot[:,2],color='k',fmt='.',marker='None')
            plt.plot(phot[:,0],phot[:,1],'o',color=self.ztf_filt_col[filter_name],label=filter_name,ms=12)

        # Plot upper limits
        for filter_id, filter_name in zip([1,2,3],['g','r','i']):
            phot = np.array( lc.get_ntuples(['jd','diffmaglim'],upper_limits=True,
                              filters={'attribute':'fid','operator':'==','value':filter_id}) )
            if len(phot)==0:
                continue
            plt.plot(phot[:,0],phot[:,1],'v',markeredgecolor=self.ztf_filt_col[filter_name],ms=10,markerfacecolor='None')

        
        plt.legend(loc='best')
        plt.xlabel('JD')
        plt.ylabel('Alert mag')
        plt.gca().invert_yaxis()

        a = plt.axis()
        #print(a)

        # Gather statistics 
#        ax2 = fig.add_subplot(gs[0, 2])
#        ax2 = fig.add_subplot(gs[0,2])
#        ax2 = fig.add_subplot(1,2,2)



        for propcount, aprop in enumerate(self.display_props):
            val = np.mean( lc.get_values(aprop) )
            plt.text(a[1]+(a[1]-a[0])*0.1,a[3]-propcount*(a[3]-a[2])/len(self.display_props),'%s  %.2f'%(aprop,val),horizontalalignment='left',fontsize=15)
    
 #       plt.axis([0,1,0,len(self.display_props)*0.12])
        #plt.axis('off')
 #       fig.canvas.draw()
    
        # Print t2 outputs if selected
        for tvrec in tv.t2records:
            # Check if we want to print this
            if not tvrec.get_t2_unit_id() in self.display_t2s:
                continue
            last_result = tvrec.get_results()[-1]
            print('t2 %s yield %s'%(tvrec.get_t2_unit_id(),last_result['output']))
            if tvrec.info['hasError']:
                print('... warning, t2 associated with error')
    
        return None


