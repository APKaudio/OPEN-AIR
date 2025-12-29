<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class MeterTest
    Inherits System.Windows.Forms.Form

    'Form overrides dispose to clean up the component list.
    <System.Diagnostics.DebuggerNonUserCode()> _
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
    <System.Diagnostics.DebuggerStepThrough()> _
    Private Sub InitializeComponent()
		Me.Horizontal_Meter_With_Text1 = New APK_Bench_Software.Horizontal_Meter_With_Text()
		Me.TextBox = New System.Windows.Forms.TextBox()
		Me.Button1 = New System.Windows.Forms.Button()
		Me.Label1 = New System.Windows.Forms.Label()
		Me.TrackBar1 = New System.Windows.Forms.TrackBar()
		Me.Vertical_Meter1 = New APK_Bench_Software.Vertical_Meter()
		Me.TrackBar2 = New System.Windows.Forms.TrackBar()
		Me.TrackBar3 = New System.Windows.Forms.TrackBar()
		Me.TrackBar4 = New System.Windows.Forms.TrackBar()
		CType(Me.TrackBar1, System.ComponentModel.ISupportInitialize).BeginInit()
		CType(Me.TrackBar2, System.ComponentModel.ISupportInitialize).BeginInit()
		CType(Me.TrackBar3, System.ComponentModel.ISupportInitialize).BeginInit()
		CType(Me.TrackBar4, System.ComponentModel.ISupportInitialize).BeginInit()
		Me.SuspendLayout()
		'
		'Horizontal_Meter_With_Text1
		'
		Me.Horizontal_Meter_With_Text1.BackColor = System.Drawing.SystemColors.ControlDark
		Me.Horizontal_Meter_With_Text1.Location = New System.Drawing.Point(81, 118)
		Me.Horizontal_Meter_With_Text1.ModuleNumber = 0R
		Me.Horizontal_Meter_With_Text1.Name = "Horizontal_Meter_With_Text1"
		Me.Horizontal_Meter_With_Text1.Size = New System.Drawing.Size(632, 324)
		Me.Horizontal_Meter_With_Text1.TabIndex = 0
		Me.Horizontal_Meter_With_Text1.Title_To_Display = Nothing
		Me.Horizontal_Meter_With_Text1.Value_To_Display = 0R
		'
		'TextBox
		'
		Me.TextBox.Location = New System.Drawing.Point(178, 39)
		Me.TextBox.Name = "TextBox"
		Me.TextBox.Size = New System.Drawing.Size(100, 20)
		Me.TextBox.TabIndex = 1
		Me.TextBox.Text = "123.456789"
		'
		'Button1
		'
		Me.Button1.Location = New System.Drawing.Point(585, 220)
		Me.Button1.Name = "Button1"
		Me.Button1.Size = New System.Drawing.Size(75, 23)
		Me.Button1.TabIndex = 2
		Me.Button1.Text = "Button1"
		Me.Button1.UseVisualStyleBackColor = True
		'
		'Label1
		'
		Me.Label1.AutoSize = True
		Me.Label1.Location = New System.Drawing.Point(515, 45)
		Me.Label1.Name = "Label1"
		Me.Label1.Size = New System.Drawing.Size(208, 13)
		Me.Label1.TabIndex = 3
		Me.Label1.Text = "if the number is -ve it should got right to left"
		'
		'TrackBar1
		'
		Me.TrackBar1.Location = New System.Drawing.Point(155, 484)
		Me.TrackBar1.Maximum = 100
		Me.TrackBar1.Name = "TrackBar1"
		Me.TrackBar1.Size = New System.Drawing.Size(181, 45)
		Me.TrackBar1.TabIndex = 4
		'
		'Vertical_Meter1
		'
		Me.Vertical_Meter1.Location = New System.Drawing.Point(337, 118)
		Me.Vertical_Meter1.ModuleNumber = 0R
		Me.Vertical_Meter1.Name = "Vertical_Meter1"
		Me.Vertical_Meter1.Plot_V1 = 0R
		Me.Vertical_Meter1.Plot_V2 = 0R
		Me.Vertical_Meter1.Plot_V3 = 0R
		Me.Vertical_Meter1.Plot_V4 = 0R
		Me.Vertical_Meter1.Size = New System.Drawing.Size(176, 454)
		Me.Vertical_Meter1.TabIndex = 5
		'
		'TrackBar2
		'
		Me.TrackBar2.Location = New System.Drawing.Point(155, 541)
		Me.TrackBar2.Maximum = 3550
		Me.TrackBar2.Name = "TrackBar2"
		Me.TrackBar2.Size = New System.Drawing.Size(181, 45)
		Me.TrackBar2.TabIndex = 6
		'
		'TrackBar3
		'
		Me.TrackBar3.Location = New System.Drawing.Point(518, 490)
		Me.TrackBar3.Maximum = 1000
		Me.TrackBar3.Name = "TrackBar3"
		Me.TrackBar3.Size = New System.Drawing.Size(181, 45)
		Me.TrackBar3.TabIndex = 7
		'
		'TrackBar4
		'
		Me.TrackBar4.Location = New System.Drawing.Point(518, 541)
		Me.TrackBar4.Maximum = 1000
		Me.TrackBar4.Name = "TrackBar4"
		Me.TrackBar4.Size = New System.Drawing.Size(181, 45)
		Me.TrackBar4.TabIndex = 8
		'
		'MeterTest
		'
		Me.AutoScaleDimensions = New System.Drawing.SizeF(6.0!, 13.0!)
		Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
		Me.ClientSize = New System.Drawing.Size(763, 645)
		Me.Controls.Add(Me.TrackBar4)
		Me.Controls.Add(Me.TrackBar3)
		Me.Controls.Add(Me.TrackBar2)
		Me.Controls.Add(Me.Vertical_Meter1)
		Me.Controls.Add(Me.TrackBar1)
		Me.Controls.Add(Me.Label1)
		Me.Controls.Add(Me.Button1)
		Me.Controls.Add(Me.TextBox)
		Me.Controls.Add(Me.Horizontal_Meter_With_Text1)
		Me.Name = "MeterTest"
		Me.Text = "MeterTest"
		CType(Me.TrackBar1, System.ComponentModel.ISupportInitialize).EndInit()
		CType(Me.TrackBar2, System.ComponentModel.ISupportInitialize).EndInit()
		CType(Me.TrackBar3, System.ComponentModel.ISupportInitialize).EndInit()
		CType(Me.TrackBar4, System.ComponentModel.ISupportInitialize).EndInit()
		Me.ResumeLayout(False)
		Me.PerformLayout()

	End Sub

	Friend WithEvents Horizontal_Meter_With_Text1 As Horizontal_Meter_With_Text
    Friend WithEvents TextBox As TextBox
    Friend WithEvents Button1 As Button
    Friend WithEvents Label1 As Label
    Friend WithEvents TrackBar1 As TrackBar
    Friend WithEvents Vertical_Meter1 As Vertical_Meter
    Friend WithEvents TrackBar2 As TrackBar
    Friend WithEvents TrackBar3 As TrackBar
    Friend WithEvents TrackBar4 As TrackBar
End Class
