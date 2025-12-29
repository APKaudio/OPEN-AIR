<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()>
Partial Class SoundSource
	Inherits System.Windows.Forms.UserControl

	'UserControl overrides dispose to clean up the component list.
	<System.Diagnostics.DebuggerNonUserCode()>
	Protected Overrides Sub Dispose(ByVal disposing As Boolean)
		Try
			If disposing AndAlso components IsNot Nothing Then
				components.Dispose()
			End If
		Finally
			MyBase.Dispose(disposing)
		End Try
	End Sub

	'Required by the Windows Form Designer
	Private components As System.ComponentModel.IContainer

	'NOTE: The following procedure is required by the Windows Form Designer
	'It can be modified using the Windows Form Designer.  
	'Do not modify it using the code editor.
	<System.Diagnostics.DebuggerStepThrough()>
	Private Sub InitializeComponent()
		Me.Label11 = New System.Windows.Forms.Label()
		Me.SigGen_Sine_freq = New System.Windows.Forms.TextBox()
		Me.TextBox_TimeUnits = New System.Windows.Forms.TextBox()
		Me.Label_TimeBase = New System.Windows.Forms.Label()
		Me.SigGen_Signal_Type = New System.Windows.Forms.ComboBox()
		Me.Label13 = New System.Windows.Forms.Label()
		Me.Label14 = New System.Windows.Forms.Label()
		Me.SigGen_DutyCycle = New System.Windows.Forms.TrackBar()
		Me.SigGen_Amp_unit = New System.Windows.Forms.ComboBox()
		Me.SigGen_amp = New System.Windows.Forms.TextBox()
		Me.ButtSignalOnOff = New System.Windows.Forms.Button()
		Me.SigGen_FrequencyTrackBar = New System.Windows.Forms.TrackBar()
		Me.QuickFreq10Hz = New System.Windows.Forms.RadioButton()
		Me.QuickFreq500Hz = New System.Windows.Forms.RadioButton()
		Me.QuickFreq100Hz = New System.Windows.Forms.RadioButton()
		Me.QuickFreq200Hz = New System.Windows.Forms.RadioButton()
		Me.QuickFreq1kHz = New System.Windows.Forms.RadioButton()
		Me.QuickFreq50Hz = New System.Windows.Forms.RadioButton()
		Me.QuickFreq20Hz = New System.Windows.Forms.RadioButton()
		Me.QuickFreq5kHz = New System.Windows.Forms.RadioButton()
		Me.QuickFreq2kHz = New System.Windows.Forms.RadioButton()
		Me.TableLayoutPanel1 = New System.Windows.Forms.TableLayoutPanel()
		Me.RadioButton1 = New System.Windows.Forms.RadioButton()
		Me.QuickFreq50kHz = New System.Windows.Forms.RadioButton()
		Me.QuickFreq20kHz = New System.Windows.Forms.RadioButton()
		Me.QuickFreq10kHz = New System.Windows.Forms.RadioButton()
		Me.QuickFreq100kHz = New System.Windows.Forms.RadioButton()
		Me.RadioButton2 = New System.Windows.Forms.RadioButton()
		Me.TableLayoutPanel2 = New System.Windows.Forms.TableLayoutPanel()
		Me.TableLayoutPanel3 = New System.Windows.Forms.TableLayoutPanel()
		Me.TableLayoutPanel4 = New System.Windows.Forms.TableLayoutPanel()
		CType(Me.SigGen_DutyCycle, System.ComponentModel.ISupportInitialize).BeginInit()
		CType(Me.SigGen_FrequencyTrackBar, System.ComponentModel.ISupportInitialize).BeginInit()
		Me.TableLayoutPanel1.SuspendLayout()
		Me.TableLayoutPanel2.SuspendLayout()
		Me.TableLayoutPanel3.SuspendLayout()
		Me.TableLayoutPanel4.SuspendLayout()
		Me.SuspendLayout()
		'
		'Label11
		'
		Me.Label11.AutoSize = True
		Me.Label11.Cursor = System.Windows.Forms.Cursors.WaitCursor
		Me.Label11.Font = New System.Drawing.Font("Microsoft Sans Serif", 14.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label11.Location = New System.Drawing.Point(3, 0)
		Me.Label11.Name = "Label11"
		Me.Label11.Size = New System.Drawing.Size(142, 20)
		Me.Label11.TabIndex = 204
		Me.Label11.Text = "Frequency (Hz)"
		'
		'SigGen_Sine_freq
		'
		Me.SigGen_Sine_freq.Cursor = System.Windows.Forms.Cursors.WaitCursor
		Me.SigGen_Sine_freq.Dock = System.Windows.Forms.DockStyle.Fill
		Me.SigGen_Sine_freq.Font = New System.Drawing.Font("Microsoft Sans Serif", 26.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.SigGen_Sine_freq.Location = New System.Drawing.Point(3, 23)
		Me.SigGen_Sine_freq.Name = "SigGen_Sine_freq"
		Me.SigGen_Sine_freq.Size = New System.Drawing.Size(467, 47)
		Me.SigGen_Sine_freq.TabIndex = 198
		Me.SigGen_Sine_freq.Text = "1000"
		'
		'TextBox_TimeUnits
		'
		Me.TextBox_TimeUnits.Cursor = System.Windows.Forms.Cursors.WaitCursor
		Me.TextBox_TimeUnits.Dock = System.Windows.Forms.DockStyle.Fill
		Me.TextBox_TimeUnits.Font = New System.Drawing.Font("Microsoft Sans Serif", 26.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.TextBox_TimeUnits.Location = New System.Drawing.Point(476, 23)
		Me.TextBox_TimeUnits.Name = "TextBox_TimeUnits"
		Me.TextBox_TimeUnits.Size = New System.Drawing.Size(467, 47)
		Me.TextBox_TimeUnits.TabIndex = 218
		Me.TextBox_TimeUnits.Text = "1000"
		'
		'Label_TimeBase
		'
		Me.Label_TimeBase.AutoSize = True
		Me.Label_TimeBase.Cursor = System.Windows.Forms.Cursors.WaitCursor
		Me.Label_TimeBase.Font = New System.Drawing.Font("Microsoft Sans Serif", 14.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.Label_TimeBase.Location = New System.Drawing.Point(476, 0)
		Me.Label_TimeBase.Name = "Label_TimeBase"
		Me.Label_TimeBase.Size = New System.Drawing.Size(79, 20)
		Me.Label_TimeBase.TabIndex = 219
		Me.Label_TimeBase.Text = "Time (s)"
		'
		'SigGen_Signal_Type
		'
		Me.SigGen_Signal_Type.Cursor = System.Windows.Forms.Cursors.WaitCursor
		Me.SigGen_Signal_Type.Dock = System.Windows.Forms.DockStyle.Fill
		Me.SigGen_Signal_Type.Font = New System.Drawing.Font("Microsoft Sans Serif", 15.75!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.SigGen_Signal_Type.FormattingEnabled = True
		Me.SigGen_Signal_Type.Items.AddRange(New Object() {"SIN", "SQU", "RAMP", "PULS", "NOISE"})
		Me.SigGen_Signal_Type.Location = New System.Drawing.Point(476, 185)
		Me.SigGen_Signal_Type.Name = "SigGen_Signal_Type"
		Me.SigGen_Signal_Type.Size = New System.Drawing.Size(467, 33)
		Me.SigGen_Signal_Type.TabIndex = 207
		'
		'Label13
		'
		Me.Label13.AutoSize = True
		Me.Label13.Cursor = System.Windows.Forms.Cursors.WaitCursor
		Me.Label13.Location = New System.Drawing.Point(3, 182)
		Me.Label13.Name = "Label13"
		Me.Label13.Size = New System.Drawing.Size(31, 13)
		Me.Label13.TabIndex = 208
		Me.Label13.Text = "Type"
		'
		'Label14
		'
		Me.Label14.AutoSize = True
		Me.Label14.Cursor = System.Windows.Forms.Cursors.WaitCursor
		Me.Label14.Location = New System.Drawing.Point(12, 401)
		Me.Label14.Name = "Label14"
		Me.Label14.Size = New System.Drawing.Size(22, 13)
		Me.Label14.TabIndex = 206
		Me.Label14.Text = "DC"
		'
		'SigGen_DutyCycle
		'
		Me.SigGen_DutyCycle.BackColor = System.Drawing.Color.DarkGray
		Me.SigGen_DutyCycle.Cursor = System.Windows.Forms.Cursors.WaitCursor
		Me.SigGen_DutyCycle.Dock = System.Windows.Forms.DockStyle.Fill
		Me.SigGen_DutyCycle.Location = New System.Drawing.Point(3, 764)
		Me.SigGen_DutyCycle.Maximum = 100
		Me.SigGen_DutyCycle.Name = "SigGen_DutyCycle"
		Me.SigGen_DutyCycle.Size = New System.Drawing.Size(946, 25)
		Me.SigGen_DutyCycle.TabIndex = 202
		Me.SigGen_DutyCycle.Value = 50
		'
		'SigGen_Amp_unit
		'
		Me.SigGen_Amp_unit.Cursor = System.Windows.Forms.Cursors.WaitCursor
		Me.SigGen_Amp_unit.Dock = System.Windows.Forms.DockStyle.Fill
		Me.SigGen_Amp_unit.Font = New System.Drawing.Font("Microsoft Sans Serif", 15.75!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.SigGen_Amp_unit.FormattingEnabled = True
		Me.SigGen_Amp_unit.Items.AddRange(New Object() {"Vpp", "Vrms", "dBm"})
		Me.SigGen_Amp_unit.Location = New System.Drawing.Point(476, 3)
		Me.SigGen_Amp_unit.Name = "SigGen_Amp_unit"
		Me.SigGen_Amp_unit.Size = New System.Drawing.Size(467, 33)
		Me.SigGen_Amp_unit.TabIndex = 200
		'
		'SigGen_amp
		'
		Me.SigGen_amp.Cursor = System.Windows.Forms.Cursors.WaitCursor
		Me.SigGen_amp.Dock = System.Windows.Forms.DockStyle.Fill
		Me.SigGen_amp.Font = New System.Drawing.Font("Microsoft Sans Serif", 15.75!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.SigGen_amp.Location = New System.Drawing.Point(3, 3)
		Me.SigGen_amp.Name = "SigGen_amp"
		Me.SigGen_amp.Size = New System.Drawing.Size(467, 31)
		Me.SigGen_amp.TabIndex = 199
		Me.SigGen_amp.Text = "1"
		'
		'ButtSignalOnOff
		'
		Me.ButtSignalOnOff.Cursor = System.Windows.Forms.Cursors.WaitCursor
		Me.ButtSignalOnOff.Dock = System.Windows.Forms.DockStyle.Fill
		Me.ButtSignalOnOff.Location = New System.Drawing.Point(3, 3)
		Me.ButtSignalOnOff.Name = "ButtSignalOnOff"
		Me.ButtSignalOnOff.Size = New System.Drawing.Size(946, 179)
		Me.ButtSignalOnOff.TabIndex = 209
		Me.ButtSignalOnOff.Text = "OFF"
		Me.ButtSignalOnOff.UseVisualStyleBackColor = True
		'
		'SigGen_FrequencyTrackBar
		'
		Me.SigGen_FrequencyTrackBar.Dock = System.Windows.Forms.DockStyle.Fill
		Me.SigGen_FrequencyTrackBar.Location = New System.Drawing.Point(3, 288)
		Me.SigGen_FrequencyTrackBar.Maximum = 50000
		Me.SigGen_FrequencyTrackBar.Name = "SigGen_FrequencyTrackBar"
		Me.SigGen_FrequencyTrackBar.Size = New System.Drawing.Size(946, 24)
		Me.SigGen_FrequencyTrackBar.TabIndex = 289
		'
		'QuickFreq10Hz
		'
		Me.QuickFreq10Hz.AutoSize = True
		Me.QuickFreq10Hz.Location = New System.Drawing.Point(3, 3)
		Me.QuickFreq10Hz.Name = "QuickFreq10Hz"
		Me.QuickFreq10Hz.Size = New System.Drawing.Size(50, 14)
		Me.QuickFreq10Hz.TabIndex = 290
		Me.QuickFreq10Hz.TabStop = True
		Me.QuickFreq10Hz.Text = "10Hz"
		Me.QuickFreq10Hz.UseVisualStyleBackColor = True
		'
		'QuickFreq500Hz
		'
		Me.QuickFreq500Hz.AutoSize = True
		Me.QuickFreq500Hz.Location = New System.Drawing.Point(192, 43)
		Me.QuickFreq500Hz.Name = "QuickFreq500Hz"
		Me.QuickFreq500Hz.Size = New System.Drawing.Size(56, 17)
		Me.QuickFreq500Hz.TabIndex = 295
		Me.QuickFreq500Hz.TabStop = True
		Me.QuickFreq500Hz.Text = "500Hz"
		Me.QuickFreq500Hz.UseVisualStyleBackColor = True
		'
		'QuickFreq100Hz
		'
		Me.QuickFreq100Hz.AutoSize = True
		Me.QuickFreq100Hz.Location = New System.Drawing.Point(192, 3)
		Me.QuickFreq100Hz.Name = "QuickFreq100Hz"
		Me.QuickFreq100Hz.Size = New System.Drawing.Size(56, 14)
		Me.QuickFreq100Hz.TabIndex = 293
		Me.QuickFreq100Hz.TabStop = True
		Me.QuickFreq100Hz.Text = "100Hz"
		Me.QuickFreq100Hz.UseVisualStyleBackColor = True
		'
		'QuickFreq200Hz
		'
		Me.QuickFreq200Hz.AutoSize = True
		Me.QuickFreq200Hz.Location = New System.Drawing.Point(192, 23)
		Me.QuickFreq200Hz.Name = "QuickFreq200Hz"
		Me.QuickFreq200Hz.Size = New System.Drawing.Size(56, 14)
		Me.QuickFreq200Hz.TabIndex = 294
		Me.QuickFreq200Hz.TabStop = True
		Me.QuickFreq200Hz.Text = "200Hz"
		Me.QuickFreq200Hz.UseVisualStyleBackColor = True
		'
		'QuickFreq1kHz
		'
		Me.QuickFreq1kHz.AutoSize = True
		Me.QuickFreq1kHz.Location = New System.Drawing.Point(381, 3)
		Me.QuickFreq1kHz.Name = "QuickFreq1kHz"
		Me.QuickFreq1kHz.Size = New System.Drawing.Size(50, 14)
		Me.QuickFreq1kHz.TabIndex = 296
		Me.QuickFreq1kHz.TabStop = True
		Me.QuickFreq1kHz.Text = "1kHz"
		Me.QuickFreq1kHz.UseVisualStyleBackColor = True
		'
		'QuickFreq50Hz
		'
		Me.QuickFreq50Hz.AutoSize = True
		Me.QuickFreq50Hz.Location = New System.Drawing.Point(3, 43)
		Me.QuickFreq50Hz.Name = "QuickFreq50Hz"
		Me.QuickFreq50Hz.Size = New System.Drawing.Size(50, 17)
		Me.QuickFreq50Hz.TabIndex = 292
		Me.QuickFreq50Hz.TabStop = True
		Me.QuickFreq50Hz.Text = "50Hz"
		Me.QuickFreq50Hz.UseVisualStyleBackColor = True
		'
		'QuickFreq20Hz
		'
		Me.QuickFreq20Hz.AutoSize = True
		Me.QuickFreq20Hz.Location = New System.Drawing.Point(3, 23)
		Me.QuickFreq20Hz.Name = "QuickFreq20Hz"
		Me.QuickFreq20Hz.Size = New System.Drawing.Size(50, 14)
		Me.QuickFreq20Hz.TabIndex = 291
		Me.QuickFreq20Hz.TabStop = True
		Me.QuickFreq20Hz.Text = "20Hz"
		Me.QuickFreq20Hz.UseVisualStyleBackColor = True
		'
		'QuickFreq5kHz
		'
		Me.QuickFreq5kHz.AutoSize = True
		Me.QuickFreq5kHz.Location = New System.Drawing.Point(381, 43)
		Me.QuickFreq5kHz.Name = "QuickFreq5kHz"
		Me.QuickFreq5kHz.Size = New System.Drawing.Size(50, 17)
		Me.QuickFreq5kHz.TabIndex = 298
		Me.QuickFreq5kHz.TabStop = True
		Me.QuickFreq5kHz.Text = "5kHz"
		Me.QuickFreq5kHz.UseVisualStyleBackColor = True
		'
		'QuickFreq2kHz
		'
		Me.QuickFreq2kHz.AutoSize = True
		Me.QuickFreq2kHz.Location = New System.Drawing.Point(381, 23)
		Me.QuickFreq2kHz.Name = "QuickFreq2kHz"
		Me.QuickFreq2kHz.Size = New System.Drawing.Size(50, 14)
		Me.QuickFreq2kHz.TabIndex = 297
		Me.QuickFreq2kHz.TabStop = True
		Me.QuickFreq2kHz.Text = "2kHz"
		Me.QuickFreq2kHz.UseVisualStyleBackColor = True
		'
		'TableLayoutPanel1
		'
		Me.TableLayoutPanel1.ColumnCount = 5
		Me.TableLayoutPanel1.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 20.0!))
		Me.TableLayoutPanel1.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 20.0!))
		Me.TableLayoutPanel1.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 20.0!))
		Me.TableLayoutPanel1.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 20.0!))
		Me.TableLayoutPanel1.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 20.0!))
		Me.TableLayoutPanel1.Controls.Add(Me.QuickFreq10Hz, 0, 0)
		Me.TableLayoutPanel1.Controls.Add(Me.QuickFreq100Hz, 1, 0)
		Me.TableLayoutPanel1.Controls.Add(Me.RadioButton1, 4, 1)
		Me.TableLayoutPanel1.Controls.Add(Me.QuickFreq1kHz, 2, 0)
		Me.TableLayoutPanel1.Controls.Add(Me.QuickFreq50kHz, 3, 2)
		Me.TableLayoutPanel1.Controls.Add(Me.QuickFreq20kHz, 3, 1)
		Me.TableLayoutPanel1.Controls.Add(Me.QuickFreq5kHz, 2, 2)
		Me.TableLayoutPanel1.Controls.Add(Me.QuickFreq500Hz, 1, 2)
		Me.TableLayoutPanel1.Controls.Add(Me.QuickFreq10kHz, 3, 0)
		Me.TableLayoutPanel1.Controls.Add(Me.QuickFreq2kHz, 2, 1)
		Me.TableLayoutPanel1.Controls.Add(Me.QuickFreq200Hz, 1, 1)
		Me.TableLayoutPanel1.Controls.Add(Me.QuickFreq100kHz, 4, 0)
		Me.TableLayoutPanel1.Controls.Add(Me.QuickFreq50Hz, 0, 2)
		Me.TableLayoutPanel1.Controls.Add(Me.QuickFreq20Hz, 0, 1)
		Me.TableLayoutPanel1.Controls.Add(Me.RadioButton2, 4, 2)
		Me.TableLayoutPanel1.Dock = System.Windows.Forms.DockStyle.Fill
		Me.TableLayoutPanel1.Location = New System.Drawing.Point(3, 318)
		Me.TableLayoutPanel1.Name = "TableLayoutPanel1"
		Me.TableLayoutPanel1.RowCount = 3
		Me.TableLayoutPanel1.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 20.0!))
		Me.TableLayoutPanel1.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 20.0!))
		Me.TableLayoutPanel1.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 20.0!))
		Me.TableLayoutPanel1.Size = New System.Drawing.Size(946, 69)
		Me.TableLayoutPanel1.TabIndex = 304
		'
		'RadioButton1
		'
		Me.RadioButton1.AutoSize = True
		Me.RadioButton1.Location = New System.Drawing.Point(759, 23)
		Me.RadioButton1.Name = "RadioButton1"
		Me.RadioButton1.Size = New System.Drawing.Size(62, 14)
		Me.RadioButton1.TabIndex = 303
		Me.RadioButton1.TabStop = True
		Me.RadioButton1.Text = "200kHz"
		Me.RadioButton1.UseVisualStyleBackColor = True
		'
		'QuickFreq50kHz
		'
		Me.QuickFreq50kHz.AutoSize = True
		Me.QuickFreq50kHz.Location = New System.Drawing.Point(570, 43)
		Me.QuickFreq50kHz.Name = "QuickFreq50kHz"
		Me.QuickFreq50kHz.Size = New System.Drawing.Size(56, 17)
		Me.QuickFreq50kHz.TabIndex = 301
		Me.QuickFreq50kHz.TabStop = True
		Me.QuickFreq50kHz.Text = "50kHz"
		Me.QuickFreq50kHz.UseVisualStyleBackColor = True
		'
		'QuickFreq20kHz
		'
		Me.QuickFreq20kHz.AutoSize = True
		Me.QuickFreq20kHz.Location = New System.Drawing.Point(570, 23)
		Me.QuickFreq20kHz.Name = "QuickFreq20kHz"
		Me.QuickFreq20kHz.Size = New System.Drawing.Size(56, 14)
		Me.QuickFreq20kHz.TabIndex = 300
		Me.QuickFreq20kHz.TabStop = True
		Me.QuickFreq20kHz.Text = "20kHz"
		Me.QuickFreq20kHz.UseVisualStyleBackColor = True
		'
		'QuickFreq10kHz
		'
		Me.QuickFreq10kHz.AutoSize = True
		Me.QuickFreq10kHz.Location = New System.Drawing.Point(570, 3)
		Me.QuickFreq10kHz.Name = "QuickFreq10kHz"
		Me.QuickFreq10kHz.Size = New System.Drawing.Size(56, 14)
		Me.QuickFreq10kHz.TabIndex = 299
		Me.QuickFreq10kHz.TabStop = True
		Me.QuickFreq10kHz.Text = "10kHz"
		Me.QuickFreq10kHz.UseVisualStyleBackColor = True
		'
		'QuickFreq100kHz
		'
		Me.QuickFreq100kHz.AutoSize = True
		Me.QuickFreq100kHz.Location = New System.Drawing.Point(759, 3)
		Me.QuickFreq100kHz.Name = "QuickFreq100kHz"
		Me.QuickFreq100kHz.Size = New System.Drawing.Size(62, 14)
		Me.QuickFreq100kHz.TabIndex = 302
		Me.QuickFreq100kHz.TabStop = True
		Me.QuickFreq100kHz.Text = "100kHz"
		Me.QuickFreq100kHz.UseVisualStyleBackColor = True
		'
		'RadioButton2
		'
		Me.RadioButton2.AutoSize = True
		Me.RadioButton2.Location = New System.Drawing.Point(759, 43)
		Me.RadioButton2.Name = "RadioButton2"
		Me.RadioButton2.Size = New System.Drawing.Size(62, 17)
		Me.RadioButton2.TabIndex = 304
		Me.RadioButton2.TabStop = True
		Me.RadioButton2.Text = "500kHz"
		Me.RadioButton2.UseVisualStyleBackColor = True
		'
		'TableLayoutPanel2
		'
		Me.TableLayoutPanel2.ColumnCount = 2
		Me.TableLayoutPanel2.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel2.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel2.Controls.Add(Me.Label_TimeBase, 1, 0)
		Me.TableLayoutPanel2.Controls.Add(Me.TextBox_TimeUnits, 1, 1)
		Me.TableLayoutPanel2.Controls.Add(Me.Label11, 0, 0)
		Me.TableLayoutPanel2.Controls.Add(Me.SigGen_Sine_freq, 0, 1)
		Me.TableLayoutPanel2.Dock = System.Windows.Forms.DockStyle.Fill
		Me.TableLayoutPanel2.Location = New System.Drawing.Point(3, 188)
		Me.TableLayoutPanel2.Name = "TableLayoutPanel2"
		Me.TableLayoutPanel2.RowCount = 2
		Me.TableLayoutPanel2.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 20.0!))
		Me.TableLayoutPanel2.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 20.0!))
		Me.TableLayoutPanel2.Size = New System.Drawing.Size(946, 94)
		Me.TableLayoutPanel2.TabIndex = 305
		'
		'TableLayoutPanel3
		'
		Me.TableLayoutPanel3.ColumnCount = 2
		Me.TableLayoutPanel3.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel3.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel3.Controls.Add(Me.SigGen_amp, 0, 0)
		Me.TableLayoutPanel3.Controls.Add(Me.SigGen_Amp_unit, 1, 0)
		Me.TableLayoutPanel3.Controls.Add(Me.SigGen_Signal_Type, 1, 1)
		Me.TableLayoutPanel3.Controls.Add(Me.Label13, 0, 1)
		Me.TableLayoutPanel3.Dock = System.Windows.Forms.DockStyle.Fill
		Me.TableLayoutPanel3.Location = New System.Drawing.Point(3, 393)
		Me.TableLayoutPanel3.Name = "TableLayoutPanel3"
		Me.TableLayoutPanel3.RowCount = 2
		Me.TableLayoutPanel3.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel3.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 50.0!))
		Me.TableLayoutPanel3.Size = New System.Drawing.Size(946, 365)
		Me.TableLayoutPanel3.TabIndex = 306
		'
		'TableLayoutPanel4
		'
		Me.TableLayoutPanel4.ColumnCount = 1
		Me.TableLayoutPanel4.ColumnStyles.Add(New System.Windows.Forms.ColumnStyle(System.Windows.Forms.SizeType.Percent, 100.0!))
		Me.TableLayoutPanel4.Controls.Add(Me.ButtSignalOnOff, 0, 0)
		Me.TableLayoutPanel4.Controls.Add(Me.TableLayoutPanel3, 0, 4)
		Me.TableLayoutPanel4.Controls.Add(Me.SigGen_DutyCycle, 0, 5)
		Me.TableLayoutPanel4.Controls.Add(Me.TableLayoutPanel2, 0, 1)
		Me.TableLayoutPanel4.Controls.Add(Me.TableLayoutPanel1, 0, 3)
		Me.TableLayoutPanel4.Controls.Add(Me.SigGen_FrequencyTrackBar, 0, 2)
		Me.TableLayoutPanel4.Dock = System.Windows.Forms.DockStyle.Fill
		Me.TableLayoutPanel4.Location = New System.Drawing.Point(0, 0)
		Me.TableLayoutPanel4.Name = "TableLayoutPanel4"
		Me.TableLayoutPanel4.RowCount = 6
		Me.TableLayoutPanel4.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 33.33333!))
		Me.TableLayoutPanel4.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 100.0!))
		Me.TableLayoutPanel4.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 30.0!))
		Me.TableLayoutPanel4.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 75.0!))
		Me.TableLayoutPanel4.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Percent, 66.66666!))
		Me.TableLayoutPanel4.RowStyles.Add(New System.Windows.Forms.RowStyle(System.Windows.Forms.SizeType.Absolute, 30.0!))
		Me.TableLayoutPanel4.Size = New System.Drawing.Size(952, 792)
		Me.TableLayoutPanel4.TabIndex = 307
		'
		'SoundSource
		'
		Me.AutoScaleDimensions = New System.Drawing.SizeF(6.0!, 13.0!)
		Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
		Me.BackColor = System.Drawing.SystemColors.ActiveCaption
		Me.Controls.Add(Me.TableLayoutPanel4)
		Me.Controls.Add(Me.Label14)
		Me.Name = "SoundSource"
		Me.Size = New System.Drawing.Size(952, 792)
		CType(Me.SigGen_DutyCycle, System.ComponentModel.ISupportInitialize).EndInit()
		CType(Me.SigGen_FrequencyTrackBar, System.ComponentModel.ISupportInitialize).EndInit()
		Me.TableLayoutPanel1.ResumeLayout(False)
		Me.TableLayoutPanel1.PerformLayout()
		Me.TableLayoutPanel2.ResumeLayout(False)
		Me.TableLayoutPanel2.PerformLayout()
		Me.TableLayoutPanel3.ResumeLayout(False)
		Me.TableLayoutPanel3.PerformLayout()
		Me.TableLayoutPanel4.ResumeLayout(False)
		Me.TableLayoutPanel4.PerformLayout()
		Me.ResumeLayout(False)
		Me.PerformLayout()

	End Sub
	Friend WithEvents Label11 As Label
	Friend WithEvents SigGen_Sine_freq As TextBox
	Friend WithEvents TextBox_TimeUnits As TextBox
	Friend WithEvents Label_TimeBase As Label
	Friend WithEvents SigGen_Signal_Type As ComboBox
	Friend WithEvents Label13 As Label
	Friend WithEvents Label14 As Label
	Friend WithEvents SigGen_DutyCycle As TrackBar
	Friend WithEvents SigGen_Amp_unit As ComboBox
	Friend WithEvents SigGen_amp As TextBox
	Friend WithEvents ButtSignalOnOff As Button
	Friend WithEvents SigGen_FrequencyTrackBar As TrackBar
	Friend WithEvents QuickFreq10Hz As RadioButton
	Friend WithEvents QuickFreq500Hz As RadioButton
	Friend WithEvents QuickFreq100Hz As RadioButton
	Friend WithEvents QuickFreq200Hz As RadioButton
	Friend WithEvents QuickFreq1kHz As RadioButton
	Friend WithEvents QuickFreq50Hz As RadioButton
	Friend WithEvents QuickFreq20Hz As RadioButton
	Friend WithEvents QuickFreq5kHz As RadioButton
	Friend WithEvents QuickFreq2kHz As RadioButton
	Friend WithEvents TableLayoutPanel1 As TableLayoutPanel
	Friend WithEvents TableLayoutPanel2 As TableLayoutPanel
	Friend WithEvents TableLayoutPanel3 As TableLayoutPanel
	Friend WithEvents RadioButton1 As RadioButton
	Friend WithEvents QuickFreq50kHz As RadioButton
	Friend WithEvents QuickFreq20kHz As RadioButton
	Friend WithEvents QuickFreq10kHz As RadioButton
	Friend WithEvents QuickFreq100kHz As RadioButton
	Friend WithEvents RadioButton2 As RadioButton
	Friend WithEvents TableLayoutPanel4 As TableLayoutPanel
End Class
