#!/usr/bin/perl -w

use utf8;
use Text::Balanced qw ( 
            extract_multiple
            extract_delimited
            extract_variable
            extract_bracketed );

binmode(STDIN, ":encoding(utf8)");
binmode(STDOUT, ":encoding(utf8)");
binmode(STDERR, ":encoding(utf8)");

my $zero_utf8 = '०';
my $zwnj_char = "[\x{200c}\x{200d}]";
my $hdr = <STDIN>;
$hdr =~ s/$zwnj_char//g;
chop $hdr;
#print $hdr . "\n";
my @hdrfields = split(/,/, $hdr);
my $sutra_idx = undef;
my $i = 0;
foreach my $f (@hdrfields) {
    if ($f =~ m/^Sutra_krama/i) {
        $sutra_idx = $i;
        last;
    }
    ++ $i;
}

my $ajit_notesurl =
"vyakhya";
my $avg_notesurl =
"http://avg-sanskrit.org/avgdocs/doku.php?id=sutras:";
$indent = "";
my %adhikara_end = ();

$indent = "  ";
print "{\n";
print "$indent\"sutra_attrs\" : {\n";
my @shortfields = ();
my @field_descs = ();
$i = 0;
my %field_idx = ();
foreach my $f (@hdrfields) {
    my $shortname = $f;
    $f =~ s/$//;
    $shortname =~ s/\s+.*$//;
    push @field_descs, "$indent  \"$shortname\" : \"$f\"";
    push @shortfields, $shortname;
    $field_idx{$shortname} = $i;
    ++ $i;
}
print join(",\n", @field_descs);
print "\n$indent},\n";

print "$indent\"sutras\" : {\n";
$indent .= "  ";
my $nsutras = 0;
while (<STDIN>) {
	chop;
    s/$zwnj_char//g;
	my @fields = split /,/;

    print ",\n" if $nsutras > 0;

    ++ $nsutras;
    my $sutra_num = $fields[$sutra_idx];

    my @cur_asutras = keys %adhikara_end;
    foreach my $a (@cur_asutras) {
        if ($adhikara_end{$a} < $sutra_num) {
            delete $adhikara_end{$a};
            next;
        }
    }
    my @my_asutras = keys %adhikara_end;

	print $indent . "\"$sutra_num\" : {\n";
    my $indent2 = "$indent    ";
    print "$indent2\"adhikara_from\" : [ " . join(', ', @my_asutras) . " ],\n"
        if @my_asutras;

    my @sutra_attrs = ();
    $fields[$field_idx{"PadacCheda"}] .= " || " .
            $fields[$field_idx{"SamasacCheda"}];
    for (my $i = 0; $i < @fields; ++ $i) {
        next if $shortfields[$i] =~ /^SamasacCheda/i;
        my $val = print_sutra($sutra_num, $shortfields[$i], $fields[$i], $indent2);
        if ($val) {
            push @sutra_attrs, $indent2 . "\"" . $shortfields[$i] . "\" : $val";
        }
    }
    print join(",\n", @sutra_attrs) . "\n";
	print $indent . "}";
}
print "\n  }\n";
print "}\n";
exit 0;

sub print_sutra
{
	my ($sutra_num, $name, $f, $indent) = @_;
    my $val = $f;
    if ($name =~ /^Commentary/i) {
        if ($f =~ /^(\d+)/) {
            my $chapter = $1;
            $val = "<a href=\\\"$ajit_notesurl/$chapter/$f.htm\\\" target=_new>Sktdocs-$f</a>";
        }
        my $avg_sno = $f;
        $avg_sno =~ s/\./-/g;
        $val .= "; <a href=\\\"$avg_notesurl$avg_sno\\\" target=_new>AVG-$f</a>";
    }
    elsif ($name =~ /^Influence/i) {
        if ($val) {
            my ($abegin, $aend) = split(/\-/, $val);
            $adhikara_end{$sutra_num} = $aend;
        }
    }
    elsif ($name =~ /^PadacCheda$/i) {
        if (defined $val) {
            if ($val =~ /^na\s*$/i) {
                $val = "";
            }
            elsif ($val) {
                $val = "\n" . print_json_padaccheda($val, "$indent    ");
            }
            else {
                $val = "missing";
            }
        }
    }
    elsif ($name =~ /^anuvrtti/i) {
        if (defined $val) {
            if ($val =~ /^na\s*$/i) {
                $val = "";
            }
            elsif ($val) {
                $val = "\n" . print_json_anuvrttis($val, "$indent    ");
            }
            else {
                $val = "missing";
            }
        }
    }
    elsif ($name =~ /^Sutra_type/i) {
        if (! defined($val) || ! $val) {
            $val = "विधिः";
        }
        if ($val =~ /;/) {
            #my $types = split(/;\s*/, $val)
            $val = "[ \"" . join('", "', split(/;\s*/, $val)) . "\"]";
        }
        if ($val !~ /\[/) {
            $val = "[ \"$val\" ]";
        }
    }

    if (defined($val)) {
        $val =~ s/^\s*//; $val =~ s/\s*$//;
    }
    if ($val) {
        $val = "\"$val\"" unless $val =~ /^\d+$/ || $val =~ /^[\[\{]/;
    }
    return $val;
}
#end of sub

sub print_json_anuvrttis
{
	my ($anu_str, $indent) = @_;
    my $json = "";
	$json .= $indent . "[\n";
    #print $anu_str . "\n";
    my @anu_jsons = ();
	foreach my $sec (split(/\s*\|\s*/, $anu_str))
	{
		my @anufields = split(/\s*:\s*/, $sec);
        $anufields[1] =~ s/\s+$//;
        my @padas = map { "\"$_\"" } split(/\s+/, $anufields[1]);
        #print $anufields[0] . "-> {" . join(', ', @padas) . "}\n";
		push @anu_jsons, $indent . "    { \"sutra\": " . $anufields[0] . 
			", \"padas\": [" . join(', ', @padas) . "] }";
	}
    $json .= join(",\n", @anu_jsons);
    $json .= "\n$indent]\n";

    return $json;
}

sub print_pada_attrs
{
    my $indent = shift;
    my $attrs = shift;
    my @padas = @_;

    return () unless @padas;
    $attrs->{'type'} = 'तिङन्तम्' unless defined($attrs->{'type'});
    my @pada_jsons = ();
    foreach my $p (@padas) {
        $attrs->{'pada'} = $p->[0];
        $attrs->{'pada_split'} = $p->[1] if $p->[0] ne $p->[1];
        my $attr_json = $indent . "{ " .  
            join(', ', map { my $s = $_; "\"$s\" : " . 
                        (($attrs->{$s} =~ /^\d+$/) ? $attrs->{$s} 
                                                : "\"" . $attrs->{$s} . "\"")}
                            sort(keys(%$attrs))) . " }";
            push @pada_jsons, $attr_json;
    }
    return @pada_jsons;
    #map { $indent . "{ \"$_\" : $attr_json }" } @padas;
}

sub utf8_to_int
{
    my $str = shift;
    #print $str . "\n";
    my @chars = split('', $str);
    my @zero = split('', $zero_utf8);

    my $val = 0;
    foreach my $c (@chars) {
        #print "$c = " . ord($c) . ", $zero_utf8 = " . ord($zero[0]) . "\n";
        my $num = ord($c) - ord($zero[0]);
        $val = $val * 10 + $num;
    }
    if ($val > 7 || $val < 0) {
        print "Incorrect Number = $str $val\n";
    }
        
    return $val;
}

sub print_json_padaccheda
{
	my ($pada_str, $indent) = @_;
    my $json = "";

    my ($pada_val, $samasa_val) = split(/\s*\|\|\s*/, $pada_str);
    #print "padaccheda = " . $pada_str . "\n";
	$json .= $indent . "[\n";
    my $indent2 = "$indent    ";

    #print "$pada_str\n";
    my @components = extract_multiple($pada_val,
        [
            sub { extract_bracketed($_[0],'()') },
            qr/\s*([^\s]+)\s*/,
        ]);
    my @samasa_components = extract_multiple($samasa_val,
        [
            sub { extract_bracketed($_[0],'()') },
            qr/\s*([^\s]+)\s*/,
        ]);

    #print join("\n", @components) . "\n";

    my %pada_attrs = ();
    my @padas = ();
    my $emit = 0;
    my @pada_jsons = ();
    for (my $i = 0; $i < @components; ++ $i) {
        $c = $components[$i];
        $samasa_c = $samasa_components[$i];
        if ($c =~ /^\(/) {
            $c =~ s/^\(//; $c =~ s/\)$//;
            $pada_attrs{'comment'} = $c;
            $emit = 1;
        }
        elsif ($c =~ m|(.*?)/(.*)|) {
            my ($vibhakti, $vachana) = ($1, $2);
            $vibhakti = utf8_to_int($vibhakti);
            $vachana = utf8_to_int($vachana);
            $pada_attrs{'vibhakti'} = $vibhakti;
            $pada_attrs{'vachana'} = $vachana;
            if ($vibhakti == 0 && $vachana == 0) {
                $pada_attrs{'type'} = 'अव्यय';
            }
            else {
                $pada_attrs{'type'} = 'सुबन्त';
            }
            $emit = 1;
        }
        else {
            if ($emit) {
                push @pada_jsons, print_pada_attrs($indent2, \%pada_attrs, @padas);
                %pada_attrs = ();
                @padas = ();
                $emit = 0;
            }
            push @padas, [$c, $samasa_c];
        }
    }
    push @pada_jsons, print_pada_attrs($indent2, \%pada_attrs, @padas) 
        if @padas;
    $json .= join(",\n", @pada_jsons);
    $json .= "\n$indent]\n";

    return $json;
}
