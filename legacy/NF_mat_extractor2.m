%% Written by Tom Coopmans, 2020
% Script promts user for .mat file, reads the amount of channels, prompts
% the user for channel to use if more than one. Extracts data and expports
% it into Excel file. Tested with IO curve, tetanus and normal stimulation. IO curve
% extraction states the stimulus strength in the first row of the IO part of
% the table.

%Create data files
warning('off','all')                                    %supress warnings
clear all
file = uigetfile('*.mat', 'Select a mat file:');
Data = load(file);
Channels_available = [];
%disp(Data.Device.kanalen)                              %Diagnostic
for i = 1:16
    if Data.Device.kanalen(i) == 1
        Channels_available(end+1) = i;
    end
end
%auto select if 1 channel
if size(Channels_available) == 1
    Channelselect = Channels_available(1);
else %show available channels and ask for channel select
    fprintf('Available channels are:')
    disp(Channels_available)
    prompt = 'What channel would you like to select?     ';
    Channelselect = input(prompt);
end
Exportchannel = Channelselect - Channels_available(1) + 1;
Voltage = Data.Device.adcdata(:,Exportchannel);         %Voltage data
Time = reshape(Data.Device.adcas,[],1);                 %Time data
if strcmp(Data.Device.mode,'IO') == 1
%     Voltage(2:end+1) = Voltage;
%     Voltage(1) = 0;
    Time(2:end+1) = Time;
    Time(1) = 0;    
    fprintf('IO curve found. This part is slow. \nPlease be patient..... \n')
    IOdata = squeeze(Data.Device.adcset(:,Exportchannel,:));
    IOsize = size(IOdata,2);
    Samples = size(IOdata,1);
    Stimintermediate = struct2cell(Data.Device.cmd);
    Stim = reshape(squeeze(cell2mat(Stimintermediate(4,1,:))),1,[]);
    IO = zeros(Samples+1,IOsize);
    IO(1,:) = Stim;
    IO(2:Samples+1,:) = IOdata;
    ExportTable = table(Time, IO);
elseif strcmp(Data.Device.mode,'IT') == 1
    Time(2:end+1) = Time;
    Time(1) = 0;    
    fprintf('IT curve found. This part is slow. \nPlease be patient..... \n')
    ITdata = squeeze(Data.Device.adcset(:,Exportchannel,:));
    ITsize = size(ITdata,2);
    Samples = size(ITdata,1);
    DeltaTintermediate = struct2cell(Data.Device.cmd);
    DeltaT1 = reshape(squeeze(cell2mat(DeltaTintermediate(1,1,:))),1,[]);
    DeltaT2 = reshape(squeeze(cell2mat(DeltaTintermediate(2,1,:))),1,[]);
    DeltaT = DeltaT2 - DeltaT1;
    IT = zeros(Samples+1,ITsize);
    IT(1,:) = DeltaT;
    IT(2:Samples+1,:) = ITdata;
    ExportTable = table(Time, IT);
else
    ExportTable = table(Voltage, Time);
end
extention = '.xlsx';                                    %Create filename
extension = '.csv';
filenamesplit = strsplit(file, '.');
filename = char(filenamesplit(1));
Savefilename = strcat(filename,extention);
writetable(ExportTable,Savefilename);                  %save into .xlsx file
csvname = strcat(filename, extension);
writetable(ExportTable, csvname);
fprintf('Done! Excel file is saved in this folder. \n')
warning('on','all')                                     %Reset warning state

