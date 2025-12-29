<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class DCLoadForm
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
	<System.Diagnostics.DebuggerStepThrough()>
	Private Sub InitializeComponents()
		Me.BusttonDCLoadApplied = New System.Windows.Forms.Button()
		Me.BarGraphVoltage = New System.Windows.Forms.ProgressBar()
		Me.AppliedResistance = New System.Windows.Forms.TrackBar()
		Me.AppliedResistanceExact = New System.Windows.Forms.TextBox()
		Me.BarGraphCurrent = New System.Windows.Forms.ProgressBar()
		Me.BarGraphPower = New System.Windows.Forms.ProgressBar()
		Me.ReadVoltage = New System.Windows.Forms.Label()
		Me.ReadCurrent = New System.Windows.Forms.Label()
		Me.ReadPower = New System.Windows.Forms.Label()
		Me.Button1 = New System.Windows.Forms.Button()
		Me.Label1 = New System.Windows.Forms.Label()
		Me.ValueNumberPower = New System.Windows.Forms.Label()
		Me.ValueNumberCurrent = New System.Windows.Forms.Label()
		Me.ValueNumberVoltage = New System.Windows.Forms.Label()
		Me.ValueNumberResistance = New System.Windows.Forms.Label()
		Me.Label5 = New System.Windows.Forms.Label()
		Me.BarGraphResistance = New System.Windows.Forms.ProgressBar()
		CType(Me.AppliedResistance, System.ComponentModel.ISupportInitialize).BeginInit()
		Me.SuspendLayout()
		'
		'BusttonDCLoadApplied
		'
		Me.BusttonDCLoadApplied.BackColor = System.Drawing.Color.RoyalBlue
		Me.BusttonDCLoadApplied.Font = New System.Drawing.Font("Microsoft Sans Serif", 27.75!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.BusttonDCLoadApplied.ForeColor = System.Drawing.Color.Black
		Me.BusttonDCLoadApplied.Location = New System.Drawing.Point(19, 153)
		Me.BusttonDCLoadApplied.Name = "BusttonDCLoadApplied"
		Me.BusttonDCLoadApplied.Size = New System.Drawing.Size(354, 88)
		Me.BusttonDCLoadApplied.TabIndex = 0
		Me.BusttonDCLoadApplied.Text = "Load Applied"
		Me.BusttonDCLoadApplied.UseVisualStyleBackColor = False
		'
		'BarGraphVoltage
		'
		Me.BarGraphVoltage.Location = New System.Drawing.Point(20, 247)
		Me.BarGraphVoltage.Maximum = 60
		Me.BarGraphVoltage.Name = "BarGraphVoltage"
		Me.BarGraphVoltage.Size = New System.Drawing.Size(272, 44)
		Me.BarGraphVoltage.TabIndex = 1
		'
		'AppliedResistance
		'
		Me.AppliedResistance.LargeChange = 50
		Me.AppliedResistance.Location = New System.Drawing.Point(5, 57)
		Me.AppliedResistance.Maximum = 999
		Me.AppliedResistance.Minimum = 1
		Me.AppliedResistance.Name = "AppliedResistance"
		Me.AppliedResistance.Size = New System.Drawing.Size(368, 45)
		Me.AppliedResistance.TabIndex = 2
		Me.AppliedResistance.Value = 999
		'
		'AppliedResistanceExact
		'
		Me.AppliedResistanceExact.Font = New System.Drawing.Font("Microsoft Sans Serif", 24.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.AppliedResistanceExact.Location = New System.Drawing.Point(83, 12)
		Me.AppliedResistanceExact.Name = "AppliedResistanceExact"
		Me.AppliedResistanceExact.Size = New System.Drawing.Size(290, 44)
		Me.AppliedResistanceExact.TabIndex = 3
		Me.AppliedResistanceExact.Text = "1000"
		'
		'BarGraphCurrent
		'
		Me.BarGraphCurrent.Location = New System.Drawing.Point(20, 292)
		Me.BarGraphCurrent.Maximum = 10
		Me.BarGraphCurrent.Name = "BarGraphCurrent"
		Me.BarGraphCurrent.Size = New System.Drawing.Size(272, 44)
		Me.BarGraphCurrent.TabIndex = 4
		'
		'BarGraphPower
		'
		Me.BarGraphPower.Location = New System.Drawing.Point(20, 337)
		Me.BarGraphPower.Name = "BarGraphPower"
		Me.BarGraphPower.Size = New System.Drawing.Size(272, 44)
		Me.BarGraphPower.TabIndex = 5
		'
		'ReadVoltage
		'
		Me.ReadVoltage.AutoSize = True
		Me.ReadVoltage.BackColor = System.Drawing.Color.Transparent
		Me.ReadVoltage.ForeColor = System.Drawing.SystemColors.ButtonFace
		Me.ReadVoltage.Location = New System.Drawing.Point(26, 277)
		Me.ReadVoltage.Name = "ReadVoltage"
		Me.ReadVoltage.Size = New System.Drawing.Size(43, 13)
		Me.ReadVoltage.TabIndex = 6
		Me.ReadVoltage.Text = "Voltage"
		Me.ReadVoltage.TextAlign = System.Drawing.ContentAlignment.TopCenter
		'
		'ReadCurrent
		'
		Me.ReadCurrent.AutoSize = True
		Me.ReadCurrent.BackColor = System.Drawing.Color.Transparent
		Me.ReadCurrent.ForeColor = System.Drawing.SystemColors.ButtonFace
		Me.ReadCurrent.Location = New System.Drawing.Point(26, 323)
		Me.ReadCurrent.Name = "ReadCurrent"
		Me.ReadCurrent.Size = New System.Drawing.Size(41, 13)
		Me.ReadCurrent.TabIndex = 7
		Me.ReadCurrent.Text = "Current"
		Me.ReadCurrent.TextAlign = System.Drawing.ContentAlignment.TopCenter
		'
		'ReadPower
		'
		Me.ReadPower.AutoSize = True
		Me.ReadPower.BackColor = System.Drawing.Color.Transparent
		Me.ReadPower.ForeColor = System.Drawing.SystemColors.ButtonFace
		Me.ReadPower.Location = New System.Drawing.Point(26, 369)
		Me.ReadPower.Name = "ReadPower"
		Me.ReadPower.Size = New System.Drawing.Size(37, 13)
		Me.ReadPower.TabIndex = 8
		Me.ReadPower.Text = "Power"
		Me.ReadPower.TextAlign = System.Drawing.ContentAlignment.TopCenter
		'
		'Button1
		'
		Me.Button1.Location = New System.Drawing.Point(303, 247)
		Me.Button1.Name = "Button1"
		Me.Button1.Size = New System.Drawing.Size(75, 134)
		Me.Button1.TabIndex = 9
		Me.Button1.Text = "ButtonDCLoadRead"
		Me.Button1.UseVisualStyleBackColor = True
		'
		'Label1
		'
		Me.Label1.AutoSize = True
		Me.Label1.ForeColor = System.Drawing.SystemColors.ButtonFace
		Me.Label1.Location = New System.Drawing.Point(17, 29)
		Me.Label1.Name = "Label1"
		Me.Label1.Size = New System.Drawing.Size(60, 13)
		Me.Label1.TabIndex = 10
		Me.Label1.Text = "Resistance"
		Me.Label1.TextAlign = System.Drawing.ContentAlignment.TopCenter
		'
		'ValueNumberPower
		'
		Me.ValueNumberPower.Anchor = CType((((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Bottom) _
			Or System.Windows.Forms.AnchorStyles.Left) _
			Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
		Me.ValueNumberPower.AutoSize = True
		Me.ValueNumberPower.BackColor = System.Drawing.Color.Transparent
		Me.ValueNumberPower.Font = New System.Drawing.Font("Microsoft Sans Serif", 15.75!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.ValueNumberPower.ForeColor = System.Drawing.Color.Transparent
		Me.ValueNumberPower.Location = New System.Drawing.Point(100, 337)
		Me.ValueNumberPower.Name = "ValueNumberPower"
		Me.ValueNumberPower.Size = New System.Drawing.Size(166, 25)
		Me.ValueNumberPower.TabIndex = 11
		Me.ValueNumberPower.Text = "POWER VALUE"
		Me.ValueNumberPower.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'ValueNumberCurrent
		'
		Me.ValueNumberCurrent.Anchor = CType((((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Bottom) _
			Or System.Windows.Forms.AnchorStyles.Left) _
			Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
		Me.ValueNumberCurrent.AutoSize = True
		Me.ValueNumberCurrent.BackColor = System.Drawing.Color.Transparent
		Me.ValueNumberCurrent.Font = New System.Drawing.Font("Microsoft Sans Serif", 15.75!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.ValueNumberCurrent.ForeColor = System.Drawing.Color.Transparent
		Me.ValueNumberCurrent.Location = New System.Drawing.Point(100, 292)
		Me.ValueNumberCurrent.Name = "ValueNumberCurrent"
		Me.ValueNumberCurrent.Size = New System.Drawing.Size(189, 25)
		Me.ValueNumberCurrent.TabIndex = 12
		Me.ValueNumberCurrent.Text = "CURRENT VALUE"
		Me.ValueNumberCurrent.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'ValueNumberVoltage
		'
		Me.ValueNumberVoltage.Anchor = CType((((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Bottom) _
			Or System.Windows.Forms.AnchorStyles.Left) _
			Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
		Me.ValueNumberVoltage.AutoSize = True
		Me.ValueNumberVoltage.BackColor = System.Drawing.Color.Transparent
		Me.ValueNumberVoltage.Font = New System.Drawing.Font("Microsoft Sans Serif", 15.75!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.ValueNumberVoltage.ForeColor = System.Drawing.Color.Transparent
		Me.ValueNumberVoltage.Location = New System.Drawing.Point(100, 247)
		Me.ValueNumberVoltage.Name = "ValueNumberVoltage"
		Me.ValueNumberVoltage.Size = New System.Drawing.Size(186, 25)
		Me.ValueNumberVoltage.TabIndex = 13
		Me.ValueNumberVoltage.Text = "VOLTAGE VALUE"
		Me.ValueNumberVoltage.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'ValueNumberResistance
		'
		Me.ValueNumberResistance.Anchor = CType((((System.Windows.Forms.AnchorStyles.Top Or System.Windows.Forms.AnchorStyles.Bottom) _
			Or System.Windows.Forms.AnchorStyles.Left) _
			Or System.Windows.Forms.AnchorStyles.Right), System.Windows.Forms.AnchorStyles)
		Me.ValueNumberResistance.AutoSize = True
		Me.ValueNumberResistance.BackColor = System.Drawing.Color.Transparent
		Me.ValueNumberResistance.Font = New System.Drawing.Font("Microsoft Sans Serif", 15.75!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
		Me.ValueNumberResistance.ForeColor = System.Drawing.Color.Transparent
		Me.ValueNumberResistance.Location = New System.Drawing.Point(100, 99)
		Me.ValueNumberResistance.Name = "ValueNumberResistance"
		Me.ValueNumberResistance.Size = New System.Drawing.Size(220, 25)
		Me.ValueNumberResistance.TabIndex = 16
		Me.ValueNumberResistance.Text = "RESISTANCE VALUE"
		Me.ValueNumberResistance.TextAlign = System.Drawing.ContentAlignment.MiddleRight
		'
		'Label5
		'
		Me.Label5.AutoSize = True
		Me.Label5.BackColor = System.Drawing.Color.Transparent
		Me.Label5.ForeColor = System.Drawing.SystemColors.ButtonFace
		Me.Label5.Location = New System.Drawing.Point(26, 129)
		Me.Label5.Name = "Label5"
		Me.Label5.Size = New System.Drawing.Size(60, 13)
		Me.Label5.TabIndex = 15
		Me.Label5.Text = "Resistance"
		Me.Label5.TextAlign = System.Drawing.ContentAlignment.TopCenter
		'
		'BarGraphResistance
		'
		Me.BarGraphResistance.Location = New System.Drawing.Point(20, 99)
		Me.BarGraphResistance.Maximum = 1000
		Me.BarGraphResistance.Name = "BarGraphResistance"
		Me.BarGraphResistance.Size = New System.Drawing.Size(353, 44)
		Me.BarGraphResistance.TabIndex = 14
		'
		'DCLoadForm
		'
		Me.AutoScaleDimensions = New System.Drawing.SizeF(6.0!, 13.0!)
		Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
		Me.BackColor = System.Drawing.Color.FromArgb(CType(CType(0, Byte), Integer), CType(CType(0, Byte), Integer), CType(CType(64, Byte), Integer))
		Me.ClientSize = New System.Drawing.Size(390, 404)
		Me.Controls.Add(Me.ValueNumberResistance)
		Me.Controls.Add(Me.Label5)
		Me.Controls.Add(Me.BarGraphResistance)
		Me.Controls.Add(Me.ValueNumberVoltage)
		Me.Controls.Add(Me.ValueNumberCurrent)
		Me.Controls.Add(Me.ValueNumberPower)
		Me.Controls.Add(Me.Label1)
		Me.Controls.Add(Me.Button1)
		Me.Controls.Add(Me.ReadPower)
		Me.Controls.Add(Me.ReadCurrent)
		Me.Controls.Add(Me.ReadVoltage)
		Me.Controls.Add(Me.BarGraphPower)
		Me.Controls.Add(Me.BarGraphCurrent)
		Me.Controls.Add(Me.AppliedResistanceExact)
		Me.Controls.Add(Me.AppliedResistance)
		Me.Controls.Add(Me.BarGraphVoltage)
		Me.Controls.Add(Me.BusttonDCLoadApplied)
		Me.Name = "DCLoadForm"
		Me.Text = "DCLoadForm"
		CType(Me.AppliedResistance, System.ComponentModel.ISupportInitialize).EndInit()
		Me.ResumeLayout(False)
		Me.PerformLayout()

	End Sub

	Friend WithEvents BusttonDCLoadApplied As Button
    Friend WithEvents BarGraphVoltage As ProgressBar
    Friend WithEvents AppliedResistance As TrackBar
    Friend WithEvents AppliedResistanceExact As TextBox
    Friend WithEvents BarGraphCurrent As ProgressBar
    Friend WithEvents BarGraphPower As ProgressBar
    Friend WithEvents ReadVoltage As Label
    Friend WithEvents ReadCurrent As Label
    Friend WithEvents ReadPower As Label
    Friend WithEvents Button1 As Button
    Friend WithEvents Label1 As Label
    Friend WithEvents ValueNumberPower As Label
    Friend WithEvents ValueNumberCurrent As Label
    Friend WithEvents ValueNumberVoltage As Label
    Friend WithEvents ValueNumberResistance As Label
    Friend WithEvents Label5 As Label
    Friend WithEvents BarGraphResistance As ProgressBar
End Class
