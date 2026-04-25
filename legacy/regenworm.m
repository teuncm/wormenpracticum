function varargout = regenworm(varargin)
% REGENWORM M-file for regenworm.fig
%      REGENWORM, by itself, creates a new REGENWORM or raises the existing
%      singleton*.
%
%      H = REGENWORM returns the handle to a new REGENWORM or the handle to
%      the existing singleton*.
%
%      REGENWORM('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in REGENWORM.M with the given input arguments.
%
%      REGENWORM('Property','Value',...) creates a new REGENWORM or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before regenworm_OpeningFunction gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to regenworm_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES
% Edit the above text to modify the response to help regenworm
% Last Modified by GUIDE v2.5 27-Oct-2009 01:35:46
% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
    'gui_Singleton',  gui_Singleton, ...
    'gui_OpeningFcn', @regenworm_OpeningFcn, ...
    'gui_OutputFcn',  @regenworm_OutputFcn, ...
    'gui_LayoutFcn',  [] , ...
    'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end
if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT

function regenworm_OpeningFcn(hObject, eventdata, handles, varargin)
    global backgroundcolor
    handles.output = hObject;
    guidata(hObject, handles);
    backgroundcolor = get(handles.Single,'BackgroundColor');
    device_Callback(hObject, eventdata, handles);
    Drawstim(handles);
    Redraw(handles)

function varargout = regenworm_OutputFcn(hObject, eventdata, handles)
    varargout{1} = handles.output;

function Activate(handle)
    set(handle,'BackgroundColor',[1.0 0.8 0.8]);

function Notfilled(handle)
    set(handle,'BackgroundColor',[0.8 0.8 1.0]);

function Deactivate(handle)
    global backgroundcolor
    set(handle,'BackgroundColor',backgroundcolor);

function [out] = Active(handle)
    global backgroundcolor
    cc = get(handle,'BackgroundColor');
    out = cc(1)>(0.5*(1+backgroundcolor(1)));

function device_Callback(hObject, eventdata, handles)
    global Device
    troep = [];
    % troep = daqfind();
    % troep = daq.getDevices();
    % if ~isempty(troep)
    %     stop(troep)
    %     delete(troep)
    %     clear troep
    %     out = daqhwinfo('nidaq');
    %     [col, numbrd] = size(out.BoardNames);
    % end

    % out = daqhwinfo('nidaq');
    % [col, numbrd] = size(out.BoardNames);
    %
    % if numbrd==0
    %     disp('No ADC devices present!')
    %     CreateStruct.Interpreter = 'tex';
    %     CreateStruct.WindowStyle = 'modal';
    %     virtualDeviceMessage = {'\fontsize{14}Geen wormenbak gevonden!', ...
    %         'Om metingen te doen dien je een wormenbak aan te sluiten' ...
    %         'en het programma opnieuw op te starten.', ...
    %         'Data analyse is wel mogelijk zonder wormenbak.'};
    %     h = warndlg(virtualDeviceMessage, 'No ADC device detected',CreateStruct);
    %     uiwait(h);
    % end
    if ~isempty(troep)
        Device = [];
        Device.name          = char(out.InstalledBoardIds(board));
        %
        ai                   = analoginput('nidaq',Device.name);
        ai.InputType         = 'SingleEnded';
        infos                = daqhwinfo(ai);
        Device.adcresolution = infos.Bits;
        Device.adcmax        = infos.TotalChannels;
        Device.adcminrate    = infos.MinSampleRate;
        Device.adcmaxrate    = infos.MaxSampleRate;
        Device.adcranges     = infos.InputRanges;
        Device.adcgains      = infos.Gains;
        %
        ao                   = analogoutput('nidaq',Device.name);
        infos                = daqhwinfo(ao);
        Device.dacresolution = infos.Bits;
        Device.dacmax        = infos.TotalChannels;
        Device.dacminrate    = infos.MinSampleRate;
        Device.dacmaxrate    = infos.MaxSampleRate;
        Device.dacranges     = infos.OutputRanges;
        Device.yrange        = [-10 10];
        Device.ymax          = Device.yrange * 1000/500;
        Device.dacrate       = 500000;
        Device.adcrate       = 250000/16;

        delete([ai ao]);
        clear ai ao dio;
        %
        Device.dio    = digitalio('nidaq',Device.name);
        hwinfo        = daqhwinfo(Device.dio);
        Device.lines1 = addline(Device.dio,0:(length(hwinfo.Port(1).LineIDs)-1),0,'Out');
        Device.lines2 = addline(Device.dio,0:(length(hwinfo.Port(2).LineIDs)-1),1,'In');
        Device.lines3 = addline(Device.dio,0:(length(hwinfo.Port(3).LineIDs)-1),2,'Out');
        Device.lines  = [Device.lines1; Device.lines3];
        Device.len    = length(Device.lines);
        Device.val1   = 0;
        Device.val3   = 128;
        %
        writedigital
        tbit = find(getvalue(Device.lines2)==1);
        Device.val3   = 0;
        disp(sprintf('Device = %s Boardname = %s',out.BoardNames{board},Device.name));
        disp(sprintf('   ADC-channels %02u  %4u kHz',Device.adcmax,Device.adcmaxrate/1000));
        disp(sprintf('   DAC-channels %02u  %4u kHz',Device.dacmax,Device.dacmaxrate/1000));
        disp(sprintf('   Digital ports 1-2-3 contain  %u %u %u bits',length(Device.lines1),length(Device.lines2),length(Device.lines3)));
        if isempty(tbit)
            Device.Triggerbit = [];     disp('   Trigger is not connected');
        elseif tbit == 1
            Device.Triggerbit = 'PFI0'; disp('   Internal trigger on bit PF0');
        elseif tbit == 2
            Device.Triggerbit = 'PFI1'; disp('   Internal trigger on bit PF1');
        end
        Device.stim1   = 1;
        Device.stim2   = 2;
        Device.kanalen = [1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1];
        for ii = 1:16
            Device.namen{ii} = sprintf('%02u',ii);
        end
        Device.cnt     = 0;
        Device.cur1    = 1;
        Device.cur2    = 2;
        Device.shape   = [];
        Device.adcdata = [];
        Device.dacdata = [];
        Device.mean    = [];
        Device.std     = [];
        Device.Sy      = [];
        Device.Syy     = [];
        Device.adcset  = [];

    elseif isempty(troep) %% In case no device is detected
        disp('No ADC devices present!')
        CreateStruct.Interpreter = 'tex';
        CreateStruct.WindowStyle = 'modal';
        virtualDeviceMessage = {'\fontsize{14}Geen wormenbak gevonden!', ...
            'Om metingen te doen dien je een wormenbak aan te sluiten' ...
            'en het programma opnieuw op te starten.', ...
            'Data analyse is wel mogelijk zonder wormenbak.'};
        h = warndlg(virtualDeviceMessage, 'No ADC device detected',CreateStruct);
        uiwait(h);
        %% Create virual recording device
        Device = [];
        Device.name          = 'VirtualDevice';
        %
        % ai                   = analoginput('nidaq',Device.name);
        % ai.InputType         = 'SingleEnded';
        % infos                = daqhwinfo(ai);
        Device.adcresolution = 16;
        Device.adcmax        = 16;
        Device.adcminrate    = 0.6;
        Device.adcmaxrate    = 250000;
        Device.adcranges     = [-10 10; -5 5; -1 1; -.2 .2];
        Device.adcgains      = [1 2 10 50];
        %
        % ao                   = analogoutput('nidaq',Device.name);
        % infos                = daqhwinfo(ao);
        Device.dacresolution = 16;
        Device.dacmax        = 2;
        Device.dacminrate    = .6;
        Device.dacmaxrate    = 833000;
        Device.dacranges     = [-10 10];
        Device.yrange        = [-10 10];
        Device.ymax          = [-20 20] * 1000/500;
        Device.dacrate       = 500000;
        Device.adcrate       = 250000/16;

        % delete([ai ao]);
        % clear ai ao dio;
        % %
        % Device.dio    = digitalio('nidaq',Device.name);
        % hwinfo        = daqhwinfo(Device.dio);
        % Device.lines1 = addline(Device.dio,0:(length(hwinfo.Port(1).LineIDs)-1),0,'Out');
        % Device.lines2 = addline(Device.dio,0:(length(hwinfo.Port(2).LineIDs)-1),1,'In');
        % Device.lines3 = addline(Device.dio,0:(length(hwinfo.Port(3).LineIDs)-1),2,'Out');
        % Device.lines  = [Device.lines1; Device.lines3];
        % Device.len    = length(Device.lines);
        % Device.val1   = 0;
        % Device.val3   = 128;
        % %
        % writedigital
        % tbit = find(getvalue(Device.lines2)==1);
        % Device.val3   = 0;
        % disp(sprintf('Device = %s Boardname = %s',out.BoardNames{board},Device.name));
        % disp(sprintf('   ADC-channels %02u  %4u kHz',Device.adcmax,Device.adcmaxrate/1000));
        % disp(sprintf('   DAC-channels %02u  %4u kHz',Device.dacmax,Device.dacmaxrate/1000));
        % disp(sprintf('   Digital ports 1-2-3 contain  %u %u %u bits',length(Device.lines1),length(Device.lines2),length(Device.lines3)));
        % if isempty(tbit)
        %     Device.Triggerbit = [];     disp('   Trigger is not connected');
        % elseif tbit == 1
        %     Device.Triggerbit = 'PFI0'; disp('   Internal trigger on bit PF0');
        % elseif tbit == 2
        %     Device.Triggerbit = 'PFI1'; disp('   Internal trigger on bit PF1');
        % end
        Device.stim1   = 1;
        Device.stim2   = 2;
        Device.kanalen = [1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1];
        for ii = 1:16
            Device.namen{ii} = sprintf('%02u',ii);
        end
        Device.cnt     = 0;
        Device.cur1    = 1;
        Device.cur2    = 2;
        Device.shape   = [];
        Device.adcdata = [];
        Device.dacdata = [];
        Device.mean    = [];
        Device.std     = [];
        Device.Sy      = [];
        Device.Syy     = [];
        Device.adcset  = [];
    else
        disp('Hmm, something went wrong')
    end
    drawworm(handles)

function writedigital
    global Device
    value = round(Device.val3);
    if value>(2^length(Device.lines3)-1)
        Cerror('DIO error','port3 < 256','did not write dio, please repot');
        value = 0;
    end
    if value<128, value = value + 128; end
    value = round(Device.val1) + value * 2^length(Device.lines1);
    putvalue(Device.lines, dec2binvec(value,Device.len));

function writedigitalstart
    global Device
    value = round(Device.val3);
    if value>(2^length(Device.lines3)-1)
        Cerror('DIO error','port3 < 256','did not write dio, please repot');
        value = 0;
    end
    if value>127, value = value - 128; end
    value = round(Device.val1) + value * 2^length(Device.lines1);
    putvalue(Device.lines, dec2binvec(value,Device.len));

function Resetbutton_Callback(hObject, eventdata, handles)
    clc
    Deactivate(handles.Single);
    timerfindall;
    % daqfind;
    if ~isempty(timerfindall)
        stop(timerfindall);
        delete(timerfindall);
    end
    if ~isempty(daq.getDevices)
        stop(daqfind);
        delete(daqfind);
        clear ai ao;
    end
    device_Callback(hObject, eventdata, handles);

function drawworm(handles)
    global Device
    axes(handles.electrode_select);
    cla(handles.electrode_select,'reset');
    hold on;
    axis([-1.5 3.5 0.5 16.5]);
    axis off;
    wsize = 14;
    yel = 1:16;
    xel = zeros(1,16);
    electroden = find(Device.kanalen == 1);
    plot(xel,  yel,'go','LineWidth',1,'Markersize',wsize,'ButtonDownFcn',{@Wormklik,handles});
    plot(xel(electroden),yel(electroden),'go','LineWidth',2,'Markersize',wsize,...
        'MarkerFaceColor','g','MarkerEdgeColor','m','ButtonDownFcn',{@Wormklik,handles});
    for ii=1:16
        text(xel(ii)-1.0,yel(ii),sprintf('%02u',ii),'Fontsize',8,'Fontname','Courier','HorizontalAlignment','center');
    end
    plot(xel+1,yel,'bo','LineWidth',2,'Markersize',wsize,'ButtonDownFcn',{@Wormklik,handles});
    if Device.stim1>0
        plot(xel(Device.stim1)+1,yel(Device.stim1),'ob','LineWidth',2,'Markersize',wsize,...
            'MarkerFaceColor','b','ButtonDownFcn',{@Wormklik,handles});
    end
    plot(xel+2,yel,'ro','LineWidth',2,'Markersize',wsize,'ButtonDownFcn',{@Wormklik,handles});
    if Device.stim2>0
        plot(xel(Device.stim2)+2,yel(Device.stim2),'or','LineWidth',2,'Markersize',wsize,...
            'MarkerFaceColor','r','ButtonDownFcn',{@Wormklik,handles});
    end
    drawnow();
    %
function makeworm(handles)
    global Device
    nulcode = 16 + 32 + 64 + 128;
    wselect = 0;
    if Device.stim1>1
        wselect = wselect + (Device.stim1-1);
        nulcode = nulcode - 32;
    end
    if Device.stim2>1
        wselect = wselect + (Device.stim2-1) * 16;
        nulcode = nulcode - 64;
    end
    Device(1).val1 = round(wselect);
    Device(1).val3 = round(nulcode);

function showbits()
    global Device
    disp(sprintf('stim1= %2.0f   stim2= %2.0f',  Device.stim1,Device.stim2));
    disp(sprintf('port1 = %12.0f  port3 = %6.0f',Device.val1, Device.val3));

function Wormklik(src,eventdata,handles)
    global Device
    fha    = get(gcbo,'Parent');
    Ppoint = get(fha,'CurrentPoint');
    xp     = round(Ppoint(1,1));
    yp     = round(round(Ppoint(1,2)));
    switch xp
        case 0
            Device.kanalen(yp) = 1-Device.kanalen(yp);
        case 1
            Device.stim1 = yp;
            if Device.stim2 == yp
                Device.stim2 = yp+1;
                if Device.stim2>16, Device.stim2 = 1; end
            end
        case 2
            Device.stim2 = yp;
            if Device.stim1 == yp
                Device.stim1 = yp+1;
                if Device.stim1>16, Device.stim1 = 1; end
            end
        otherwise
    end
    makeworm(handles);
    drawworm(handles);

function [tijduit] = rounddac(tijdin)
    global Device
    tijduit = max(1/Device.dacrate,round(tijdin*Device.dacrate)/Device.dacrate);

function [tijduit] = roundadc(tijdin)
    global Device
    tijduit = max(1/Device.adcrate,round(tijdin*Device.adcrate)/Device.adcrate);

function Drawstim(handles)
    stimplus = rounddac(str2double(get(handles.Stim_plus,'String')));
    set(handles.Stim_plus,'String',num2str(stimplus));
    hoogte  = str2double(get(handles.Intensiteit1,'String'));
    xt=zeros(8,1);
    yt=xt;
    xt(2)=0.2;
    xt(3)=xt(2);
    xt(4)=xt(3) + stimplus;
    yt(3:4)=hoogte;
    xt(5)=xt(4);
    xt(6)=xt(5) + stimplus;
    yt(5:6)=-hoogte;
    xt(7)=xt(6);
    xt(8)=xt(7)+0.2;
    axes(handles.stimshape);
    plot(xt,yt);
    axis([xt(1) xt(8) -abs(hoogte) abs(hoogte)]);
    axis off
    drawnow();

function Stim_plus_Callback(hObject, eventdata, handles)
    Drawstim(handles)

function StopADC()
    global ai ao dio
    try
        stop(ai);
        delete(ai);
        clear ai;
    catch
    end
    try
        stop(dao);
        delete(ao);
        clear ao;
    catch
    end
    try
        stop(dio);
        delete(dio);
        clear dio;
    catch
    end
    %
    % =============================================================
    %
function Analyse_Callback(hObject, eventdata, handles)
    Activate(handles.Analyse)
    Deactivate(handles.Showset);
    Deactivate(handles.Showmean)
    set([handles.analysepanel],'Visible','off');
    set(handles.meanpanel,'Visible','on');
    Doanalyse(handles);

function Showmean_Callback(hObject, eventdata, handles)
    Deactivate(handles.Showset);
    Deactivate(handles.Analyse)
    Activate (handles.Showmean)
    set([handles.meanpanel],'Visible','off');
    set(handles.analysepanel,'Visible','on');
    Drawmean(handles)

function Showset_Callback(hObject, eventdata, handles)
    Activate(handles.Showset);
    Deactivate(handles.Analyse)
    Deactivate (handles.Showmean)
    set([handles.meanpanel handles.analysepanel],'Visible','off');
    Drawset(handles);

    % =============================================================

function Redraw(handles)
    if Active(handles.Single), return; end

    Drawdata(handles)

    if     Active(handles.Analyse)
        Doanalyse(handles);
    elseif Active(handles.Showset)
        Drawset(handles);
    elseif Active(handles.Showmean)
        Drawmean(handles)
    end

function onderdeel_Callback(hObject, eventdata, handles)


function amplitude_slider_Callback(hObject, eventdata, handles)
    Redraw(handles)

function channel_Callback(hObject, eventdata, handles)
    Redraw(handles)

function Intensiteit1_Callback(hObject, eventdata, handles)
    Drawstim(handles)

function full_Callback(hObject, eventdata, handles)
    set(handles.linker,'String','0');
    set(handles.rechter,'String','inf');
    Redraw(handles)

function linker_Callback(hObject, eventdata, handles)
    Redraw(handles)

function rechter_Callback(hObject, eventdata, handles)
    Redraw(handles)

function metsd_Callback(hObject, eventdata, handles)
    if get(handles.metsd,'Value'), set(handles.metsem,'Value',0); end
    Drawmean(handles)

function metsem_Callback(hObject, eventdata, handles)
    if get(handles.metsem,'Value'), set(handles.metsd,'Value',0); end
    Drawmean(handles)

function sdgain_Callback(hObject, eventdata, handles)
    Drawmean(handles)

function Savebutton_Callback(hObject, eventdata, handles)
    global Device
    persistent filecount
    if isempty(filecount)
        filecount=1;
    else
        filecount=filecount+1;
    end
    filename = uiputfile('*.mat','save EPfile',sprintf('Worm-%03u.mat',filecount));
    save(filename,'Device');

function Loadbutton_Callback(hObject, eventdata, handles)
    filename = uigetfile('*.mat','load EPfile','Worm-xxx.mat');
    if filename ~= 0
        global Device
        load(filename,'Device');
        Drawdata(handles);
        Drawset(handles);
    end

function calculatespeed(handles)
    afstand = 3 * abs(str2double(get(handles.kanaal1,'String'))-str2double(get(handles.kanaal2,'String'))  );
    tijd = str2double(get(handles.Dx,'String'));
    if tijd~= 0
        set(handles.speed,'String',sprintf('%5.2f',abs(afstand/tijd)));
    end

function kanaal1_Callback(hObject, eventdata, handles)
    calculatespeed(handles)

function kanaal2_Callback(hObject, eventdata, handles)
    calculatespeed(handles)

function Gaussem(handles)
    global Device
    gaussw = 0.001 * Device.adcrate * str2double(get(handles.gauss,'String'));
    if gaussw>0
        gauss=[];
        done=0;
        width=1;
        total=0;
        while ~done
            gauss(width)=exp(-((width-1)*(width-1))/(2*gaussw*gaussw));
            total=total+gauss(width);
            if (gauss(width)/total)<0.01
                done=1;
            end
            width=width+1;
        end
        gauss =[gauss(width-1:-1:2) 1 gauss(2:width-1)];
        gauss = gauss'/sum(gauss);
        [row col]=size(Device.adcdata);
        for ii=1:col
            Device.adcdata(:,ii)=convn(Device.adcdata(:,ii),gauss,'same');
        end;
    end

function gauss_Callback(hObject, eventdata, handles)
    Redraw(handles)

function gausson_Callback(hObject, eventdata, handles)
    Redraw(handles)

function [xmin xmax]=Xscaling(xas,handles)
    xmin = max(xas(1),  str2double(get(handles.linker,'String')));
    xmax = min(xas(end),str2double(get(handles.rechter,'String')));
    if xmin>=xmax
        xmin=xas(1);
        set(handles.linker,'String','0');
    end
    if xmax==0
        xmax=xas(end);
        set(handles.linker,'String','inf');
    end

function [ymin ymax offset] = Yscaling(handles)
    global Device
    [row col] = size(Device.adcdata);
    gain      = 1 + 9 * get(handles.amplitude_slider,'Value');
    ymin      = -Device.ymax(2)/gain;
    ymax      = ymin + (col+1) * -ymin;
    offset    = (0:1:col-1) * -ymin;

function min_Callback(hObject, eventdata, handles)
    if get(handles.min,'Value')
        set([handles.pnt handles.max handles.piekpiek handles.mean],'Value',0)
    end
    Redraw(handles)

function max_Callback(hObject, eventdata, handles)
    if get(handles.max,'Value')
        set([handles.pnt handles.min handles.piekpiek handles.mean],'Value',0)
    end
    Redraw(handles)

function pnt_Callback(hObject, eventdata, handles)
    if get(handles.pnt,'Value')
        set([handles.min handles.max handles.piekpiek handles.mean handles.looptijd],'Value',0);
    end
    Redraw(handles)

function piekpiek_Callback(hObject, eventdata, handles)
    if get(handles.piekpiek,'Value')
        set([handles.pnt handles.min handles.max handles.mean handles.looptijd],'Value',0);
    end
    Redraw(handles)

function mean_Callback(hObject, eventdata, handles)
    if get(handles.mean,'Value')
        set([handles.pnt handles.min handles.max handles.piekpiek handles.looptijd],'Value',0);
    end
    Redraw(handles)

function plaats_Callback(hObject, eventdata, handles)
    if get(handles.plaats,'Value')
        set([handles.default handles.looptijd],'Value',0)
    end
    Redraw(handles)

function default_Callback(hObject, eventdata, handles)
    if get(handles.default,'Value')
        set([handles.plaats handles.looptijd],'Value',0);
    end
    Redraw(handles)

function looptijd_Callback(hObject, eventdata, handles)
    if get(handles.looptijd,'Value')
        set([handles.plaats handles.default handles.pnt handles.piekpiek handles.mean],'Value',0);
    end
    Redraw(handles)

function Doanalyse(handles)
    global Device
    if isempty(Device.adcset), return; end
    elektrode = round(str2double(get(handles.channel,'String')));
    kk = find(Device.channel==elektrode);
    if isempty(kk)
        uiwait(msgbox(sprintf('Elektrode %u is niet gemeten',elektrode),' Fout','modal'));
        return;
    else
        channel = kk(1);
    end
    p1 = min(Device.cur1,Device.cur2);
    p2 = max(Device.cur1,Device.cur2);
    Device.cur1 = p1;
    Device.cur2 = p2;
    set(handles.p1,'String',sprintf('%4.3f',p1));
    set(handles.p2,'String',sprintf('%4.3f',p2));
    p1 = round(0.001 * Device.adcrate * p1)+1;
    p2 = round(0.001 * Device.adcrate * p2)+1;
    [xmin xmax]=Xscaling(Device.adcas,handles);
    if strcmp(get(handles.result_1),'on')==0
        axes(handles.result_3)
        cla(handles.result_3,'reset')
        set(handles.result_1,'Visible','on');
        set(handles.result_2,'Visible','on');
        set(handles.result_3,'Visible','off');
    end

    if get(handles.default,'Value')
        yy = squeeze(Device.adcset(:,channel,:));
    else
        yy = Device.mean;
    end
    [row plane] = size(yy);
    Etext = ['Elektrode ' num2str(elektrode)];
    space   = 10;
    starty  = - space * (plane-1)/2;
    maxy    = 10 + space * (plane-1)/2;
    gain    = 1 + 9 * get(handles.amplitude_slider,'Value');
    axes(handles.result_1)
    cla(handles.result_1,'reset')
    hold on
    for kk=1:plane
        offset=starty + space * (kk-1);
        plot(Device.adcas,gain*yy(:,kk)+offset,'b','ButtonDownFcn',{@Setmuis,handles});
        plot([xmin xmax],[offset offset],':k','ButtonDownFcn',{@Setmuis,handles});
        showchan = 'on';
        if get(handles.plaats,'Value')||get(handles.looptijd,'Value')
            showchan = 'off'; Etext = 'Doorsnede';
            Sdis=sprintf('pos = %2.0f mm',3 * (Device.channel(kk)-1));
        elseif strcmp(Device.mode,'IT')
            Sdis=sprintf('dT = %5.3f ms',Device.cmd(kk).time2-Device.cmd(kk).time1);
        elseif strcmp(Device.mode,'IO')
            Sdis=sprintf('I = %5.3f V',Device.cmd(kk).amp1);
        else
            Sdis = '';
        end
        set([handles.channel handles.text43],'Visible',showchan);
        text(xmin+0.01*(xmax-xmin),gain*yy(1,kk)+offset+2,Sdis,'color','black','FontSize',8);
    end
    line([Device.adcas(p1) Device.adcas(p1)], [-maxy maxy],'Color','r','LineStyle','--','LineWidth',2.0,'ButtonDownFcn',{@Setmuis,handles});
    if get(handles.pnt,'Value') == 0
        line([Device.adcas(p2) Device.adcas(p2)], [-maxy maxy],'Color','m','LineStyle','--','LineWidth',2.0,'ButtonDownFcn',{@Setmuis,handles});
    end
    text(xmin + 0.01*(xmax-xmin),0.95*maxy,Etext,'color','black','FontSize',12);
    axis([xmin xmax -maxy maxy]);
    grid on
    drawnow;
    ys=zeros(plane,1);
    xs=zeros(plane,1);
    ps=zeros(plane,1);
    for ii=1:plane
        offset=starty + space * (ii-1);
        if get(handles.pnt,'Value')
            ys(ii) = yy(p1,ii);
            plot(Device.adcas(p1),gain*yy(p1,ii)+offset,'ro','MarkerSize',6,'Linewidth',2);
        elseif get(handles.max,'Value')
            [ys(ii) ps(ii)] = max(yy(p1:p2,ii));
            plot(Device.adcas(p1+ps(ii)-1),gain*yy(p1+ps(ii)-1,ii)+offset,'ro','MarkerSize',6,'Linewidth',2);
        elseif get(handles.min,'Value')
            [ys(ii) ps(ii)] = min(yy(p1:p2,ii));
            plot(Device.adcas(p1+ps(ii)-1),gain*yy(p1+ps(ii)-1,ii)+offset,'mo','MarkerSize',6,'Linewidth',2);
        elseif get(handles.piekpiek,'Value')
            [maxy pnt] = max(yy(p1:p2,ii));
            pnt = p1+pnt-1;
            plot(Device.adcas(pnt),gain*yy(pnt,ii)+offset,'ro','MarkerSize',6,'Linewidth',2);
            [miny pnt] = min(yy(p1:p2,ii));
            pnt = p1+pnt-1;
            plot(Device.adcas(pnt),gain*yy(pnt,ii)+offset,'mo','MarkerSize',6,'Linewidth',2);
            ys(ii) = maxy-miny;
        elseif get(handles.mean,'Value')
            ys(ii) = sum(yy(p1:p2,ii))/(p2-p1+1);
        else
            ys(ii) = sum(yy(p1:p2,ii))/(p2-p1+1);
        end
    end
    axes(handles.result_2)
    cla(handles.result_2,'reset')
    hold on
    if get(handles.plaats,'Value')
        xs = 3*([Device.channel]-1);
        xmin = min(xs);
        xmax = max(xs);
        ymin = min(ys);
        ymax = max(ys);
    elseif get(handles.looptijd,'Value')
        xs = 3*([Device.channel]-1);
        ys = ps * 1000 / Device.adcrate;
        xmin = min(xs);
        xmax = max(xs);
        ymin = min(ys);
        ymax = max(ys);
    elseif strcmp(Device.mode,'IT')
        xs = [Device.cmd.time2] - [Device.cmd.time1];
        xmin=0;
        xmax=max(xs);
        ymin=min(ys);
        ymax=max(ys);
    else
        xs = [Device.cmd.amp1];
        xmin = min(xs);
        xmax = max(xs);
        ymin = min(ys);
        ymax = max(ys);
    end
    plot(xs,ys,'-ok','MarkerSize',10,'Linewidth',2)
    dx = 0.05 * (xmax - xmin);
    dy = 0.05 * (ymax - ymin);
    if xmin == xmax, xmin = xmin - 0.5; xmax = xmax + 0.5; end
    if ymin == ymax, ymin = ymin - 0.5; ymax = ymax + 0.5; end
    grid on
    axis([xmin-dx xmax+dx ymin-dy ymax+dy])
    hold off
    drawnow;

function p1_Callback(hObject, eventdata, handles)
    global Device
    Device.cur1 = str2double(get(handles.p1,'String'));
    Device.cur2 = str2double(get(handles.p2,'String'));
    Doanalyse(handles)

function p2_Callback(hObject, eventdata, handles)
    global Device
    Device.cur1 = str2double(get(handles.p1,'String'));
    Device.cur2 = str2double(get(handles.p2,'String'));
    Doanalyse(handles)

function Setmuis(src,eventdata,handles)
    global Device
    fha    = get(gcbo,'Parent');
    Ppoint = get(fha,'CurrentPoint');
    if strcmp(get(gcf,'SelectionType'),'normal')==1
        Device.cur1 = Ppoint(1,1);
    else
        Device.cur2 = Ppoint(1,1);
    end
    Doanalyse(handles)

function Meanmuis(hObject, eventdata, handles, kanaal)
    global Device
    fha    = get(gcbo,'Parent');
    Ppoint = get(fha,'CurrentPoint');
    xpnt   = Ppoint(1,1);
    hlp = find(Device.adcas>xpnt);
    die = hlp(1);
    xpnt = Device.adcas(die);
    ypnt = Device.mean(die,kanaal);
    if strcmp(get(gcf,'SelectionType'),'normal')==1
        set(handles.P1x,'String',sprintf('%5.2f',xpnt));
        set(handles.P1y,'String',sprintf('%5.2f',ypnt));
        set(handles.Dx, 'String',sprintf('%5.2f',str2double(get(handles.P2x,'String'))-xpnt));
        set(handles.Dy, 'String',sprintf('%5.2f',str2double(get(handles.P2y,'String'))-ypnt));
        set(handles.kanaal1,'String',Device.namen{Device.channel(kanaal)});
    else
        set(handles.P2x,'String',sprintf('%5.2f',xpnt));
        set(handles.P2y,'String',sprintf('%5.2f',ypnt));
        set(handles.Dx, 'String',sprintf('%5.2f',xpnt-str2double(get(handles.P1x,'String'))));
        set(handles.Dy, 'String',sprintf('%5.2f',ypnt-str2double(get(handles.P1y,'String'))));
        set(handles.kanaal2,'String',Device.namen{Device.channel(kanaal)});
    end
    set(handles.percentage,'String',sprintf('%5.1f',100*str2double(get(handles.P2y,'String'))/str2double(get(handles.P1y,'String'))));
    calculatespeed(handles)
    set(gcf,'Pointer','arrow');

function Datamuis(hObject, eventdata, handles)
    global Device
    fha  = get(gcbo,'Parent');
    Ppoint = get(fha,'CurrentPoint');
    xpnt =Ppoint(1,1);
    if strcmp(get(gcf,'SelectionType'),'normal')==1
        set(handles.linker,'String',num2str(round(Device.adcrate * xpnt)/Device.adcrate));
    else
        set(handles.rechter,'String',num2str(round(Device.adcrate * xpnt)/Device.adcrate));
    end
    Redraw(handles)
    set(gcf,'Pointer','arrow');

function Drawset(handles)
    global Device
    if isempty(Device.adcset), return; end
    [xmin xmax]=Xscaling(Device.adcas,handles);
    if strcmp(get(handles.result_3),'on')==0
        axes(handles.result_1)
        cla
        set(handles.result_1,'Visible','off');
        set(handles.result_2,'Visible','off');
        set(handles.result_3,'Visible','on');
    end
    axes(handles.result_3)
    cla (handles.result_3,'reset')
    kleur='bgrcmbgrcmbgrcmb';
    [row col plane]=size(Device.adcset);
    space = 10;
    gain   = 1+9*get(handles.amplitude_slider,'Value');
    offset = -space*(col-1)/2:space:space*(col-1)/2;
    maxy   = 10+space*(col-1)/2;
    hold on
    for kk=1:plane
        for ii=1:col
            yy=Device.adcset(:,ii,kk);
            plot(Device.adcas,gain*yy'+offset(ii),kleur(ii));
            plot([xmin xmax],[offset(ii) offset(ii)],':k');
        end
    end
    hold off
    drawnow;
    axis([xmin xmax -maxy maxy]);

function Drawmean(handles)
    global Device
    if isempty(Device.mean), return;  end
    [xmin xmax]=Xscaling(Device.adcas,handles);
    if strcmp(get(handles.result_3,'Visible'),'on')==0
        axes(handles.result_1);
        cla(handles.result_1,'reset');
        set([handles.result_1 handles.result_2],'Visible','off');
        set(handles.result_3,'Visible','on');
    end
    [row col]          = size(Device.mean);
    [ymin ymax offset] = Yscaling(handles);
    axes(handles.result_3);
    cla
    hold on
    metlijnen = 0;
    sdgain    = str2double(get(handles.sdgain,'String'));
    if Device.cnt==1
        Sdis ='Laatste meting';
    elseif  get(handles.metsd,'Value')
        Sdis   = sprintf('Gemiddelde #%2.0f �%2.0f x sd',Device.cnt,sdgain);
        metlijnen = 1;
    elseif get(handles.metsem,'Value')
        Sdis   = sprintf('Gemiddelde #%2.0f �%2.0f x sem',Device.cnt,sdgain);
        sdgain = sdgain / realsqrt(Device.cnt);
        metlijnen = 1;
    else
        Sdis = sprintf('Gemiddelde #%2.0f',Device.cnt);
    end
    for ii=1:col
        if Device.channel(ii)==Device.stim1
            line('XData',[xmin xmax],'YData',[offset(ii) offset(ii)],'Color','b','LineStyle',':','Linewidth',2);
        elseif Device.channel(ii)==Device.stim2
            line('XData',[xmin xmax],'YData',[offset(ii) offset(ii)],'Color','r','LineStyle',':','Linewidth',2);
        else
            line('XData',Device.adcas,'YData',Device.mean(:,ii)+offset(ii),'Color','b','ButtonDownFcn',{@Meanmuis,handles,ii});
            if metlijnen
                line('XData',Device.adcas,'YData',Device.mean(:,ii) + offset(ii) + sdgain * Device.std(:,ii),'Color','m','ButtonDownFcn',{@Meanmuis,handles,ii});
                line('XData',Device.adcas,'YData',Device.mean(:,ii) + offset(ii) - sdgain * Device.std(:,ii),'Color','m','ButtonDownFcn',{@Meanmuis,handles,ii});
            end;
            line('XData',[xmin xmax], 'YData',[offset(ii) offset(ii)],'Color','k','LineStyle',':','ButtonDownFcn',{@Meanmuis,handles,ii});
            text(xmin+0.02*(xmax-xmin),Device.mean(1,ii) + offset(ii)+1,Device.namen{Device.channel(ii)},'color','black','FontSize',12);
        end
    end
    text(xmin+0.01*(xmax-xmin),0.975*ymax,Sdis,'color','black','FontSize',12);
    grid on
    axis([xmin xmax ymin ymax]);
    drawnow;

function Drawdata(handles)
    global Device
    if isempty(Device.adcdata), return; end
    kleur = 'bgrcmbgrcmbgrcmb';
    [row col]          = size(Device.adcdata);
    [xmin xmax]        = Xscaling(Device.adcas,handles);
    [ymin ymax offset] = Yscaling(handles);
    axes(handles.show_result);
    cla (handles.show_result,'reset');
    for ii=1:col
        if Device.channel(ii)==Device.stim1
            line('XData',[xmin xmax],'YData',[offset(ii) offset(ii)],'Color','b','LineStyle',':','Linewidth',2);
        elseif Device.channel(ii)==Device.stim2
            line('XData',[xmin xmax],'YData',[offset(ii) offset(ii)],'Color','r','LineStyle',':','Linewidth',2);
        else
            line('XData',Device.adcas,'YData',Device.adcdata(:,ii)+offset(ii),'Color',kleur(ii),          'ButtonDownFcn',{@Datamuis,handles});
            line('XData',[xmin xmax], 'YData',[offset(ii) offset(ii)],        'Color','r','LineStyle',':','ButtonDownFcn',{@Datamuis,handles});
            text(xmin+0.01*(xmax-xmin),Device.adcdata(1,ii)+offset(ii)+0.5,Device.namen{Device.channel(ii)},'color','black','FontSize',10);
        end
    end
    axis([xmin xmax ymin ymax]);
    drawnow;

function Puls1(onoroff,handles)
    hh = [handles.Tijd1 handles.text16 handles.Intensiteit1 handles.text69];
    if onoroff
        set(hh,'Visible','on');
        set(handles.Tetanus,'Value',0);
        Tetanus(false,handles);
    else set(hh,'Visible','off'); end

function Puls2(onoroff,handles)
    hh = [handles.Tijd2 handles.text202 handles.Intensiteit2 handles.text203];
    if onoroff
        set(hh,'Visible','on');
        set(handles.Tetanus,'Value',0);
        Tetanus(false,handles);
    else set(hh,'Visible','off'); end

function Tetanus(onoroff,handles)
    hh = [handles.Pulsnumber handles.Frequency handles.text213 handles.Intensiteit3 handles.text212];
    if onoroff
        set(hh,'Visible','on');
        set([handles.Puls1 handles.Puls2],'Value',0);
        Puls1(false,handles);
        Puls2(false,handles);
    else set(hh,'Visible','off'); end

function Puls1_Callback(hObject, eventdata, handles)
    Puls1(get(handles.Puls1,'Value'),handles);

function Puls2_Callback(hObject, eventdata, handles)
    Puls2(get(handles.Puls2,'Value'),handles)

function Tetanus_Callback(hObject, eventdata, handles)
    Tetanus(get(handles.Tetanus,'Value'),handles)

function Frequency_Callback(hObject, eventdata, handles)

function Intensiteit3_Callback(hObject, eventdata, handles)

function Pulsnumber_Callback(hObject, eventdata, handles)

function Wormtimer(obj, event)
    global flag
    flag = 1;

function Middelen_Callback(hObject, eventdata, handles)
    global broken
    if get(handles.Middelen,'Value')
        broken = 1;
        set(handles.Repeat,'Value',0);
    end

function Repeat_Callback(hObject, eventdata, handles)
    global broken
    if get(handles.Repeat,'Value')
        broken = 1;
        set([handles.Middelen handles.ITcurve handles.IOcurve],'Value',0);
        set([handles.fractie handles.text145],'Visible','off');
        set([handles.aantalstappen handles.van handles.tot handles.text155],'Visible','off');
    end

function IOcurve_Callback(hObject, eventdata, handles)
    global broken
    if get(handles.IOcurve,'Value')
        broken = 1;
        set([handles.Repeat handles.ITcurve],'Value',0);
        set([handles.fractie handles.text145],'Visible','off');
        set([handles.aantalstappen handles.van handles.tot handles.text155],'Visible','on');
    end

function ITcurve_Callback(hObject, eventdata, handles)
    global broken
    if get(handles.ITcurve,'Value')
        broken = 1;
        set([handles.Repeat handles.IOcurve],'Value',0);
        set([handles.fractie handles.text145],'Visible','on');
        set([handles.aantalstappen handles.van handles.tot handles.text155],'Visible','off');
    end

function Meten(handles)
    global Device ai ao flag broken
    if strcmp(Device.name, 'VirtualDevice')
        CreateStruct.Interpreter = 'tex';
        CreateStruct.WindowStyle = 'modal';
        virtualDeviceMessage = {'\fontsize{14}Geen wormenbak gevonden!', ...
            'Om metingen te doen dient een  wormenbak aangesloten te zijn.' ...
            'Als er een apparaat is aangesloten, probeer dan het programma opnieuw op te starten.'};
        h = warndlg(virtualDeviceMessage, 'No ADC device detected',CreateStruct);
    else
        Device.cnt    = 0;
        Device.shape  = [];
        Device.mean   = [];
        Device.std    = [];
        Device.Sy     = [];
        Device.Syy    = [];
        Device.adcset = [];
        duration      = 0.001 * str2double(get(handles.Duur,'String'));
        interval      = str2double(get(handles.repeat_time,'String'));
        %
        % make adc
        %
        ai = analoginput('nidaq',Device.name);
        set(ai,'InputType','SingleEnded');
        Device.channel = find(Device.kanalen == 1);
        addchannel(ai,Device.channel-1);
        Device.adcrate = setverify(ai,'SampleRate',250000/(length(Device.channel)*str2double(get(handles.divider,'String'))));
        set(handles.samplerate,'String',sprintf('%5.1f kHz',Device.adcrate/1000));
        adcsamples  = round(Device.adcrate * duration);
        set(ai,'SamplesPerTrigger',adcsamples);
        Device.adcas = (0:(adcsamples-1))* 1000 / Device.adcrate;
        set(ai,'LoggingMode','Memory');
        for ii=1:length(Device.channel)
            ai.Channel(ii).SensorRange = [-10 10];
            ai.Channel(ii).InputRange  = Device.yrange;
            ai.Channel(ii).UnitsRange  = Device.ymax;
            ai.Channel(ii).Units       = 'mV';
        end
        ao = analogoutput('nidaq',Device.name);
        addchannel(ao,0:1);
        for ii=1:2
            ao.Channel(ii).OutputRange = [-10 10];
            ao.Channel(ii).UnitsRange  = [-10 10];
            ao.Channel(ii).Units       = 'V';
        end

        Device.dacrate = setverify(ao,'SampleRate',500000);
        dacsamples     = round(Device.dacrate * duration);
        Device.dacdata = zeros(dacsamples,2);
        set([ai ao],'TriggerType','HwDigital');
        set([ai ao],'HwDigitalTriggerSource',Device.Triggerbit);
        set(ai,'TriggerCondition','NegativeEdge');
        %
        % set timer
        %
        if interval >0.2
            tt = timer('TimerFcn',@Wormtimer,...
                'ExecutionMode','fixedRate',...
                'BusyMode','drop',...
                'Tag','running',...
                'Startdelay',0.5,...
                'Period',interval);
            start(tt);
        end
        broken    = 0;
        for kk = 1:length(Device.cmd)
            stimlen = rounddac(str2double(get(handles.Stim_plus,'String')));
            set(handles.Stim_plus,'String',num2str(stimlen));
            hlp = ones(1,round(0.001 * Device.dacrate * stimlen));
            Device.shape = [hlp -hlp]';
            Device.cnt   = 0;
            for cntswp = 1:Device.meancnt
                set(handles.cntswp,'String',sprintf('%u',cntswp));
                writedigital();
                if interval>0.2
                    flag = 0;
                    while flag == 0,
                        if broken, break; end;
                        pause(0.1)
                    end
                end
                Device.dacdata(:,1) = zeros(length(Device.dacdata),1);
                if get(handles.Puls1,'Value')
                    t1 = round(0.001 * Device.dacrate * Device.cmd(kk).time1);
                    h1 = Device.cmd(kk).amp1;
                    set(handles.Tijd1,'String',sprintf('%4.2f',Device.cmd(kk).time1));
                    set(handles.Intensiteit1,'String',sprintf('%4.3f',h1));
                    Device.dacdata(t1:(t1+length(Device.shape)-1),1) = h1 * Device.shape(:,1);
                end
                if get(handles.Puls2,'Value')
                    t2 = round(0.001 * Device.dacrate * Device.cmd(kk).time2);
                    h2 = Device.cmd(kk).amp2;
                    set(handles.Tijd2,'String',sprintf('%4.2f',Device.cmd(kk).time2));
                    set(handles.Intensiteit2,'String',sprintf('%4.3f',h2));
                    Device.dacdata(t2:(t2+length(Device.shape)-1),1) = h2 * Device.shape(:,1);
                end
                if get(handles.Tetanus,'Value')
                    t1 = round(0.001 * Device.dacrate * Device.cmd(kk).time1);
                    t2 = round(0.001 * Device.dacrate * Device.cmd(kk).time2);
                    t3 = round(0.001 * Device.dacrate * Device.cmd(kk).time3);
                    h3 = Device.cmd(kk).amp3;
                    set(handles.Intensiteit3,'String',sprintf('%4.3f',h3));
                    for iii = t1:t3:t2
                        Device.dacdata(iii:(iii+length(Device.shape)-1),1) = h3 * Device.shape(:,1);
                    end
                end
                Device.dacdata(:,2)=-Device.dacdata(:,1);
                putdata(ao,Device.dacdata)
                pause(0.05)
                start([ai ao]);
                pause(0.05);
                writedigitalstart();
                wait(ai,1 + duration);
                Device.adcdata=getdata(ai);
                stop([ai ao])
                if get(handles.gausson,'Value'), Gaussem(handles); end

                Drawdata(handles)

                Device.cnt = Device.cnt + 1;
                if Device.cnt == 1
                    Device.Sy   = Device.adcdata;
                    Device.Syy  = Device.adcdata.^2;
                    Device.mean = Device.adcdata;
                    Device.std  = 0 * Device.adcdata;
                else
                    Device.Sy   = Device.Sy  + Device.adcdata;
                    Device.Syy  = Device.Syy + Device.adcdata.^2;
                    Device.mean = Device.Sy / Device.cnt;
                    Device.std  = realsqrt(abs((Device.Syy - ((Device.Sy.^2)/Device.cnt))/(Device.cnt-1)));
                end

                Drawmean(handles)

                if broken == 1, break; end
            end
            Device.adcset(:,:,kk) = Device.mean(:,:);
            if broken == 1, break; end
        end
        if interval >0.2
            stop (tt)
            delete(tt)
            clear tt
        end
        StopADC()
        Deactivate(handles.Single)
    end

function Single_Callback(hObject, eventdata, handles)
    global Device broken
    if Active(handles.Single), broken = 1; return; end
    if get(handles.Middelen,'Value'), Device.meancnt = str2double(get(handles.Number_average,'String')); else Device.meancnt = 1; end
    Device.cmd  = [];
    if get(handles.IOcurve,'Value')
        Puls1(true,handles);
        Tetanus(false,handles);
    end
    if get(handles.ITcurve,'Value')
        Puls1(true,handles);
        Puls2(true,handles);
        Tetanus(false,handles);
    end
    t3     = 1000/str2double(get(handles.Frequency,'String'));
    number =   str2double(get(handles.Pulsnumber,'String'));
    t1     =   str2double(get(handles.Tijd1,'String'));
    t2     =   str2double(get(handles.Tijd2,'String'));
    if get(handles.Puls1,'Value') && get(handles.Puls2,'Value')
        if (max(t1,t2)+3)>str2double(get(handles.Duur,'String')), set(handles.Duur,'String',sprintf('%4.1f',max(t1,t2)+3)); end
    elseif get(handles.Puls1,'Value')
        if (t1+3)>str2double(get(handles.Duur,'String')), set(handles.Duur,'String',sprintf('%4.1f',t1+3)); end
    elseif get(handles.Puls2,'Value')
        if (t2+3)>str2double(get(handles.Duur,'String')), set(handles.Duur,'String',sprintf('%4.1f',t2+3)); end
    elseif get(handles.Tetanus,'Value')
        t1 = 1;
        t2 = t1 + t3 * number + 3;
        set(handles.Duur,'String',sprintf('%4.1f',t2));
    end
    Device.cmd(1).time1 = t1;
    Device.cmd(1).time2 = t2;
    Device.cmd(1).time3 = t3;
    Device.cmd(1).amp1  = min(str2double(get(handles.Intensiteit1,'String')), str2double(get(handles.begrenzing,'String')));
    Device.cmd(1).amp2  = min(str2double(get(handles.Intensiteit2,'String')), str2double(get(handles.begrenzing,'String')));
    Device.cmd(1).amp3  = min(str2double(get(handles.Intensiteit3,'String')), str2double(get(handles.begrenzing,'String')));
    Activate(handles.Single);
    set(hObject,'String','Stop'); drawnow();
    if get(handles.Repeat,'Value')
        Device.meancnt = inf;
    elseif get(handles.IOcurve,'Value')
        if get(handles.Middelen,'Value') && (Device.meancnt == inf)
            set(handles.Number_average,'String','1'); Device.meancnt = 1;
        end
        Device.mode = 'IO';
        Activate(handles.Intensiteit1);
        van = min(str2double(get(handles.van,'String')), str2double(get(handles.begrenzing,'String')));
        tot = min(str2double(get(handles.tot,'String')), str2double(get(handles.begrenzing,'String')));
        num = str2double(get(handles.aantalstappen,'String'));
        if num < 2, values = van; else values = van:(tot-van)/(num-1):tot; end
        for ii = 1:length(values)
            Device.cmd(ii)      = Device.cmd(1);
            Device.cmd(ii).amp1 = values(ii);
        end
    elseif get(handles.ITcurve,'Value')
        if get(handles.Middelen,'Value') && (Device.meancnt == inf)
            set(handles.Number_average,'String','1'); Device.meancnt = 1;
        end
        Device.mode = 'IT';
        Activate(handles.Tijd1);
        tinterval = t2- t1;
        for ii = 1:20
            Device.cmd(ii)       = Device.cmd(1);
            Device.cmd(ii).time1 = t2-tinterval;
            tinterval = tinterval * str2double(get(handles.fractie,'String'))/100;
            if tinterval<0.2, break; end
        end
    elseif get(handles.Middelen,'Value')
        Device.mode = 'mean';
    else
        Device.mode = 'single';
        Device.meancnt = 1;
    end
    Meten(handles);
    set(hObject,'String','Go');
    Deactivate(handles.Single);
    % set(handles.Tijd1,'String',sprintf('%4.2f',t1));
    % set(handles.Tijd1,       'BackgroundColor',[1.0 1.0 1.0]);
    % set(handles.Intensiteit1,'BackgroundColor',[1.0 1.0 1.0]);
    Redraw(handles)
