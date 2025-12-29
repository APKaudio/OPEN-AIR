<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()>
Partial Class SoundSourceWindow
	Inherits System.Windows.Forms.Form

	'Form overrides dispose to clean up the component list.
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
		Me.SoundSource1 = New APK_Bench_Software.SoundSource()
		Me.SuspendLayout()
		'
		'SoundSource1
		'
		Me.SoundSource1.BackColor = System.Drawing.SystemColors.ActiveCaption
		Me.SoundSource1.Location = New System.Drawing.Point(0, 0)
		Me.SoundSource1.Margin = New System.Windows.Forms.Padding(6)
		Me.SoundSource1.Name = "SoundSource1"
		Me.SoundSource1.Size = New System.Drawing.Size(340, 435)
		Me.SoundSource1.TabIndex = 275
		'
		'SoundSourceWindow
		'
		Me.AutoScaleDimensions = New System.Drawing.SizeF(6.0!, 13.0!)
		Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
		Me.ClientSize = New System.Drawing.Size(355, 459)
		Me.Controls.Add(Me.SoundSource1)
		Me.Name = "SoundSourceWindow"
		Me.Text = "SoundSourceWindow"
		Me.ResumeLayout(False)

	End Sub

	Friend WithEvents SoundSource1 As SoundSource
End Class
